#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <map>
#include <bitset>
#include <vector>
#include <math.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <AccelStepper.h>
#include <TMCStepper.h>

using namespace std;
using namespace TMC2130_n;

// PINS FOR TMC-SPI
#define SDO_PIN 41
#define SCK_PIN 39
#define SDI_PIN 40

// PINS FOR MOTOR 1
#define DIR1_PIN 4
#define STEP1_PIN 3
#define EN1_PIN 1
#define CS1_PIN 2
#define SW1_PIN 13

// PINS FOR MOTOR 2
#define DIR2_PIN 8
#define STEP2_PIN 7
#define EN2_PIN 5
#define CS2_PIN 6
#define SW2_PIN 14

//PINS FOR MOTOR 3
#define DIR3_PIN 12
#define STEP3_PIN 11
#define EN3_PIN 9
#define CS3_PIN 10
#define SW3_PIN 15

//PINS FOR MOTOR 4
#define DIR4_PIN 47
#define STEP4_PIN 48
#define EN4_PIN 20
#define CS4_PIN 19
#define SW4_PIN 16

//PINS FOR MOTOR 5
#define DIR5_PIN 21
#define STEP5_PIN 26
#define EN5_PIN 34
#define CS5_PIN 33
#define SW5_PIN 17

//PINS FOR MOTOR 6
#define DIR6_PIN 35
#define STEP6_PIN 36
#define EN6_PIN 38
#define CS6_PIN 37
#define SW6_PIN 18

// VALUES FOR TMC
#define STALL_VALUE 15
#define R_SENSE 0.11f

// WRITE ADDRESS
#define WRITE_ADDR 0x80

int cs_select[] = {8, 2};
// WIFI
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

//MOTOR VARIABLES
int default_steps = 200;
int mot_speed[6];
int mot_accel[6];
float mot_reduction[6];

int mot_home_speed[6];
bool mot_home_inv[6];
int mot_home_accel[6];
float mot_home_offset[6];
int mot_home_mult[6];

int mot_mcrs[6];
int mot_rms[6];
float mot_hcm[6];

// MOTOR0 VARIABLES

//Positional Arguments
float current_deg0 = 0;
float move_to_deg0 = 0;
int move_to0 = 0;

//Homing Arguments
bool home_mot0 = false;
bool second_home0 = false;
bool home_slow0 = false;


// MOTOR1 VARIABLES

//Positional Arguments
float current_deg1 = 0;
float move_to_deg1 = 0;
int move_to1 = 0;

//Homing Arguments
bool home_mot1 = false;
bool second_home1 = false;
bool home_slow1 = false;


// MOTOR2 VARIABLES

//Positional Arguments
float current_deg2 = 0;
float move_to_deg2 = 0;
int move_to2 = 0;

//Homing Arguments
bool home_mot2 = false;
bool second_home2 = false;
bool home_slow2 = false;


// MOTOR3 VARIABLES

//Positional Arguments
float current_deg3 = 0;
float move_to_deg3 = 0;
int move_to3 = 0;

//Homing Arguments
bool home_mot3 = false;
bool second_home3 = false;
bool home_slow3 = false;


// MOTOR4 VARIABLES

//Positional Arguments
float current_deg4 = 0;
float move_to_deg4 = 0;
int move_to4 = 0;

//Homing Arguments
bool home_mot4 = false;
bool second_home4 = false;
bool home_slow4 = false;


// MOTOR5 VARIABLES

//Positional Arguments
float current_deg5 = 0;
float move_to_deg5 = 0;
int move_to5 = 0;

//Homing Arguments
bool home_mot5 = false;
bool second_home5 = false;
bool home_slow5 = false;


bool can_move = false;

TMC5160Stepper driver[] = {TMC5160Stepper(CS1_PIN, R_SENSE), TMC5160Stepper(CS2_PIN, R_SENSE), TMC5160Stepper(CS3_PIN, R_SENSE), TMC5160Stepper(CS4_PIN, R_SENSE), TMC5160Stepper(CS5_PIN, R_SENSE), TMC5160Stepper(CS6_PIN, R_SENSE)};
AccelStepper stepper[] = {
  AccelStepper(1, STEP1_PIN, DIR1_PIN),
  AccelStepper(1, STEP2_PIN, DIR2_PIN),
  AccelStepper(1, STEP3_PIN, DIR3_PIN),
  AccelStepper(1, STEP4_PIN, DIR4_PIN),
  AccelStepper(1, STEP5_PIN, DIR5_PIN),
  AccelStepper(1, STEP6_PIN, DIR6_PIN)};


void initTMC5160(int mot){
  driver[mot].begin();                                                                      // Initiate pins and registeries
  driver[mot].rms_current(mot_rms[mot], mot_hcm[mot]); // Set stepper current, second parameter is hold_multiplier
  driver[mot].en_pwm_mode(1);                                                               // Enable extremely quiet stepping
  driver[mot].toff(4);                                                                      // off time
  driver[mot].blank_time(24);                                                               // blank tim
  driver[mot].pwm_autoscale(1);
  driver[mot].microsteps(mot_mcrs[mot]); // What microstep range to use
  driver[mot].ihold(18);
  driver[mot].irun(18);
  driver[mot].TPWMTHRS(20);
}

void initStepper(int mot){
  stepper[mot].setMaxSpeed(100000);
  stepper[mot].setAcceleration(100000);
  stepper[mot].setSpeed(1000);
}

void actionSwitcher(int mot, String msg){
  int str_len = msg.length();
  String act = msg.substring(1, 3);
  Serial.println("after, action " + act + ", " + "msg");
  switch (act.toInt()){
    case 02: //Set speed
      mot_speed[mot] = msg.substring(3, str_len).toInt();
      Serial.println("changed speed of " + (String)mot + ", " + (String)mot_speed[mot]);
      break;
    case 03: //Set acceleration
      mot_accel[mot] = msg.substring(3, str_len).toInt();
      Serial.println("changed acceleration of " + (String)mot + ", " + (String)mot_accel[mot]);
      break;
    case 04: //Set reduction
      mot_reduction[mot] = msg.substring(3, str_len).toFloat();
      Serial.println("changed reduction of " + (String)mot + ", " + (String)mot_reduction[mot]);
      break;
    case 11: //Set homing speed
      mot_home_speed[mot] = msg.substring(3, str_len).toInt();
      break;
    case 12: //Set inverse homing
      mot_home_inv[mot] = msg.charAt(3) == '1' ? true : false;
      break;
    case 13: //Set homing acceleration
      mot_home_accel[mot] = msg.substring(3, str_len).toInt();
      break;
    case 14: //Set homing offset
      mot_home_offset[mot] = msg.substring(3, str_len).toInt();
      break;
    case 15: //Set second homing speed mult
      mot_home_mult[mot] = msg.substring(3, str_len).toFloat();
    case 20: //Initiate TMC Driver
      initTMC5160(mot);
      break;
    case 21: //Set Microsteps
      mot_mcrs[mot] = msg.substring(3, str_len).toInt();
      break;
    case 22: //Set RMS current
      mot_rms[mot] = msg.substring(3, str_len).toInt();
      break;
    case 23: //Set hold current multiplier
      mot_hcm[mot] = msg.substring(3, str_len).toFloat();
      break;
  }
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;

  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    String msg = (char*)data;
    Serial.println(msg);
    int str_len = msg.length();
    String mot = msg.substring(0, 1);
    String act = msg.substring(1, 3);
    Serial.println("action " + act + ", " + "msg");
    switch (mot.toInt()){
      case 0:
        switch (act.toInt()){
          case 00: //Enable motor
            digitalWrite(EN1_PIN, msg.charAt(3) == '1' ? LOW : HIGH);
            break;
          case 01: //Set angle to travel to
            stepper[0].setMaxSpeed(mot_speed[0]);
            stepper[0].setAcceleration(mot_accel[0]);
            move_to_deg0 = msg.substring(3, str_len).toFloat();
            move_to0 = int((default_steps * mot_reduction[0] * mot_mcrs[0]) * (move_to_deg0 / 360));
            stepper[0].moveTo(move_to0);
            current_deg0 = move_to_deg0;
            break;
          case 10: //Start homing
            home_mot0 = true;
            stepper[0].setSpeed(mot_home_speed[0] * (mot_home_inv[0] ? -1 : 1));
            stepper[0].setMaxSpeed(mot_home_speed[0]);
            stepper[0].setAcceleration(mot_home_accel[0]);
            break;
          case 80: //Give current position
            ws.textAll((String)current_deg0);
            break;
          default:
            actionSwitcher(0, msg);
            break;
        }
        break;
      case 1:
        switch (act.toInt()){
          case 00: //Enable motor
            digitalWrite(EN2_PIN, msg.charAt(3) == '1' ? LOW : HIGH);
            break;
          case 01: //Set angle to travel to
            stepper[1].setMaxSpeed(mot_speed[1]);
            stepper[1].setAcceleration(mot_accel[1]);
            move_to_deg1 = msg.substring(3, str_len).toFloat();
            move_to1 = int((default_steps * mot_reduction[1] * mot_mcrs[1]) * (move_to_deg1 / 360));
            stepper[1].moveTo(move_to1);
            current_deg1 = move_to_deg1;
            break;
          case 10: //Start homing
            home_mot1 = true;
            stepper[1].setSpeed(mot_home_speed[1] * (mot_home_inv[1] ? -1 : 1));
            stepper[1].setMaxSpeed(mot_home_speed[1]);
            stepper[1].setAcceleration(mot_home_accel[1]);
            break;
          case 80: //Give current position
            ws.textAll((String)current_deg1);
            break;
          default:
            actionSwitcher(1, msg);
            break;
        }
        break;
      case 2:
        switch (act.toInt()){
          case 00: //Enable motor
            digitalWrite(EN3_PIN, msg.charAt(3) == '1' ? LOW : HIGH);
            break;
          case 01: //Set angle to travel to
            stepper[2].setMaxSpeed(mot_speed[2]);
            stepper[2].setAcceleration(mot_accel[2]);
            move_to_deg2 = msg.substring(3, str_len).toFloat();
            move_to2 = int((default_steps * mot_reduction[2] * mot_mcrs[2]) * (move_to_deg2 / 360));
            stepper[2].moveTo(move_to2);
            current_deg2 = move_to_deg2;
            break;
          case 10: //Start homing
            home_mot2 = true;
            stepper[2].setSpeed(mot_home_speed[2] * (mot_home_inv[2] ? -1 : 1));
            stepper[2].setMaxSpeed(mot_home_speed[2]);
            stepper[2].setAcceleration(mot_home_accel[2]);
            break;
          case 80: //Give current position
            //ws.textAll((String)current_deg2);
            ws.textAll((String)current_deg2);
            break;
          default:
            actionSwitcher(2, msg);
            break;
        }
        break;
      case 3:
        switch (act.toInt()){
          case 00: //Enable motor
            digitalWrite(EN4_PIN, msg.charAt(3) == '1' ? LOW : HIGH);
            break;
          case 01: //Set angle to travel to
            stepper[3].setMaxSpeed(mot_speed[3]);
            stepper[3].setAcceleration(mot_accel[3]);
            move_to_deg3 = msg.substring(3, str_len).toFloat();
            move_to3 = int((default_steps * mot_reduction[3] * mot_mcrs[3]) * (move_to_deg3 / 360));
            stepper[3].moveTo(move_to3);
            current_deg3 = move_to_deg3;
            break;
          case 10: //Start homing
            home_mot3 = true;
            stepper[3].setSpeed(mot_home_speed[3] * (mot_home_inv[3] ? -1 : 1));
            stepper[3].setMaxSpeed(mot_home_speed[3]);
            stepper[3].setAcceleration(mot_home_accel[3]);
            break;
          case 80: //Give current position
            ws.textAll((String)current_deg3);
            break;
          default:
            actionSwitcher(3, msg);
            break;
        }
        break;
      case 4:
        switch (act.toInt()){
          case 00: //Enable motor
            digitalWrite(EN5_PIN, msg.charAt(3) == '1' ? LOW : HIGH);
            break;
          case 01: //Set angle to travel to
            stepper[4].setMaxSpeed(mot_speed[4]);
            stepper[4].setAcceleration(mot_accel[4]);
            move_to_deg4 = msg.substring(3, str_len).toFloat();
            move_to4 = int((default_steps * mot_reduction[4] * mot_mcrs[4]) * (move_to_deg4 / 360));
            stepper[4].moveTo(move_to4);
            current_deg4 = move_to_deg4;
            break;
          case 10: //Start homing
            home_mot4 = true;
            stepper[4].setSpeed(mot_home_speed[4] * (mot_home_inv[4] ? -1 : 1));
            stepper[4].setMaxSpeed(mot_home_speed[4]);
            stepper[4].setAcceleration(mot_home_accel[4]);
            break;
          case 80: //Give current position
            ws.textAll((String)current_deg4);
            break;
          default:
            actionSwitcher(4, msg);
            break;
        }
        break;
      case 5:
        switch (act.toInt()){
          case 00: //Enable motor
            digitalWrite(EN6_PIN, msg.charAt(3) == '1' ? LOW : HIGH);
            break;
          case 01: //Set angle to travel to
            stepper[5].setMaxSpeed(mot_speed[5]);
            stepper[5].setAcceleration(mot_accel[5]);
            move_to_deg5 = msg.substring(3, str_len).toFloat();
            move_to5 = int((default_steps * mot_reduction[5] * mot_mcrs[5]) * (move_to_deg5 / 360));
            stepper[5].moveTo(move_to5);
            current_deg5 = move_to_deg5;
            break;
          case 10: //Start homing
            home_mot1 = true;
            stepper[5].setSpeed(mot_home_speed[5] * (mot_home_inv[5] ? -1 : 1));
            stepper[5].setMaxSpeed(mot_home_speed[5]);
            stepper[5].setAcceleration(mot_home_accel[5]);
            break;
          case 80: //Give current position
            ws.textAll((String)current_deg5);
            break;
          default:
            actionSwitcher(5, msg);
            break;
        }
        break;
      case 6:
        switch (act.toInt()){
          case 00:
            default_steps = msg.substring(3, str_len).toInt();
            break;
          default:
            break;
        }
        break;
      case 9:
        can_move = true;
        break;
      default:
        break;
    }
  }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      break;
    case WS_EVT_DISCONNECT:
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
      break;
    case WS_EVT_ERROR:
      break;
  }
}

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

void setup() {
  Serial.begin(115200);

  Serial.println("ESP32 is ready!");

  WiFi.mode(WIFI_AP);
  WiFi.softAP("ESP32AAA", "12345678");

  IPAddress IP = WiFi.softAPIP();
  Serial.println("AP IP adress: ");
  Serial.print(IP);

  initWebSocket();

  server.begin();

  pinMode(EN1_PIN, OUTPUT);
  pinMode(EN2_PIN, OUTPUT);
  pinMode(EN3_PIN, OUTPUT);
  pinMode(EN4_PIN, OUTPUT);
  pinMode(EN5_PIN, OUTPUT);
  pinMode(EN6_PIN, OUTPUT);

  pinMode(SW1_PIN, INPUT_PULLUP);
  pinMode(SW2_PIN, INPUT_PULLUP);
  pinMode(SW3_PIN, INPUT_PULLUP);
  pinMode(SW4_PIN, INPUT_PULLUP);
  pinMode(SW5_PIN, INPUT_PULLUP);
  pinMode(SW6_PIN, INPUT_PULLUP);
  
  SPI.begin(SCK_PIN, SDO_PIN, SDI_PIN);
  for(int i = 0; i < 6; i++)
  
  digitalWrite(EN1_PIN, HIGH);
  digitalWrite(EN2_PIN, HIGH);
  digitalWrite(EN3_PIN, HIGH);
  digitalWrite(EN4_PIN, HIGH);
  digitalWrite(EN5_PIN, HIGH);
  digitalWrite(EN6_PIN, HIGH);
}

void loop() {
  if(home_mot0 || home_mot1 || home_mot2 || home_mot3 || home_mot4 || home_mot5){
    can_move = false;
  }
  if(can_move){
    for(int i = 0; i < 6; i++){
      stepper[i].run();
    }
    
    bool stop_move = true;
    for(int i = 0; i < 6; i++){
      stop_move = stop_move && (stepper[i].distanceToGo() == 0);
    }
    can_move = !stop_move;

  }
  
  if(home_mot0){
    if(second_home0) {
      if (stepper[0].distanceToGo() == 0){
        second_home1 = false;
        stepper[0].setSpeed(mot_home_speed[0] * mot_home_mult[0] * (mot_home_inv ? 1 : -1));
      } else {
        stepper[0].run();
      }
    } else if(digitalRead(SW1_PIN) == 1) {
        stepper[0].runSpeed();
    } else {
      if(home_slow0){
        home_mot0 = false;
        home_slow0 = false;
        current_deg0 = 0;
        stepper[0].setCurrentPosition(0);
      } else {
        home_slow0 = true;
        second_home0 = true;
        stepper[0].setCurrentPosition(0);
        stepper[0].moveTo(mot_home_offset[0]);
      }
    }
  }

  if(home_mot1){
    if(second_home1) {
      if (stepper[1].distanceToGo() == 0){
        second_home1 = false;
        stepper[1].setSpeed(mot_home_speed[1] * mot_home_mult[1] * (mot_home_inv ? 1 : -1));
      } else {
        stepper[1].run();
      }
    } else if(digitalRead(SW1_PIN) == 1) {
        stepper[1].runSpeed();
    } else {
      if(home_slow1){
        home_mot1 = false;
        home_slow1 = false;
        current_deg1 = 1;
        stepper[1].setCurrentPosition(0);
      } else {
        home_slow1 = true;
        second_home1 = true;
        stepper[1].setCurrentPosition(0);
        stepper[1].moveTo(mot_home_offset[1]);
      }
    }
  }

  if(home_mot2){
    if(second_home2) {
      if (stepper[2].distanceToGo() == 0){
        second_home1 = false;
        stepper[2].setSpeed(mot_home_speed[2] * mot_home_mult[2] * (mot_home_inv ? 1 : -1));
      } else {
        stepper[2].run();
      }
    } else if(digitalRead(SW1_PIN) == 1) {
        stepper[2].runSpeed();
    } else {
      if(home_slow2){
        home_mot2 = false;
        home_slow2 = false;
        current_deg2 = 2;
        stepper[2].setCurrentPosition(0);
      } else {
        home_slow2 = true;
        second_home2 = true;
        stepper[2].setCurrentPosition(0);
        stepper[2].moveTo(mot_home_offset[2]);
      }
    }
  }

  if(home_mot3){
    if(second_home3) {
      if (stepper[3].distanceToGo() == 0){
        second_home1 = false;
        stepper[3].setSpeed(mot_home_speed[3] * mot_home_mult[3] * (mot_home_inv ? 1 : -1));
      } else {
        stepper[3].run();
      }
    } else if(digitalRead(SW1_PIN) == 1) {
        stepper[3].runSpeed();
    } else {
      if(home_slow3){
        home_mot3 = false;
        home_slow3 = false;
        current_deg3 = 3;
        stepper[3].setCurrentPosition(0);
      } else {
        home_slow3 = true;
        second_home3 = true;
        stepper[3].setCurrentPosition(0);
        stepper[3].moveTo(mot_home_offset[3]);
      }
    }
  }

  if(home_mot4){
    if(second_home4) {
      if (stepper[4].distanceToGo() == 0){
        second_home1 = false;
        stepper[4].setSpeed(mot_home_speed[4] * mot_home_mult[4] * (mot_home_inv ? 1 : -1));
      } else {
        stepper[4].run();
      }
    } else if(digitalRead(SW1_PIN) == 1) {
        stepper[4].runSpeed();
    } else {
      if(home_slow4){
        home_mot4 = false;
        home_slow4 = false;
        current_deg4 = 4;
        stepper[4].setCurrentPosition(0);
      } else {
        home_slow4 = true;
        second_home4 = true;
        stepper[4].setCurrentPosition(0);
        stepper[4].moveTo(mot_home_offset[4]);
      }
    }
  }

  if(home_mot5){
    if(second_home5) {
      if (stepper[5].distanceToGo() == 0){
        second_home1 = false;
        stepper[5].setSpeed(mot_home_speed[5] * mot_home_mult[5] * (mot_home_inv ? 1 : -1));
      } else {
        stepper[5].run();
      }
    } else if(digitalRead(SW1_PIN) == 1) {
        stepper[5].runSpeed();
    } else {
      if(home_slow5){
        home_mot5 = false;
        home_slow5 = false;
        current_deg5 = 5;
        stepper[5].setCurrentPosition(0);
      } else {
        home_slow5 = true;
        second_home5 = true;
        stepper[5].setCurrentPosition(0);
        stepper[5].moveTo(mot_home_offset[5]);
      }
    }
  }
}