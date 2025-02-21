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
#define SDO_PIN 9
#define SCK_PIN 7
#define SDI_PIN 6

// PINS FOR MOTOR 1
#define DIR1_PIN 12
#define STEP1_PIN 11
#define EN1_PIN 5
#define CS1_PIN 8
#define SW1_PIN 45

// PINS FOR MOTOR 2
#define DIR2_PIN 4
#define STEP2_PIN 3
#define EN2_PIN 1
#define CS2_PIN 2
#define SW2_PIN 46

//PINS FOR MOTOR 3
#define DIR3_PIN 16
#define STEP3_PIN 15
#define EN3_PIN 17
#define CS3_PIN 18
#define SW3_PIN 35

//PINS FOR MOTOR 4
#define DIR4_PIN 19
#define STEP4_PIN 20
#define EN4_PIN 48
#define CS4_PIN 47
#define SW4_PIN 36

//PINS FOR MOTOR 5
#define DIR5_PIN 33
#define STEP5_PIN 34
#define EN5_PIN 26
#define CS5_PIN 21
#define SW5_PIN 37

// VALUES FOR ESP
#define DEFAULT_MRES 16
#define B_DEFAULT_MRES 8
#define B_REDUCTION 20
#define ONE_ROTATION 200 * DEFAULT_MRES
#define B_ONE_ROTATION 200 * B_DEFAULT_MRES * B_REDUCTION

// HOMING VALUES
#define HOMING_OFFSET 400
#define HOMING_SPEED 1000
#define SHOMING_SPEED 200

// HOMING VALUES FOR BIG MOTOR
#define B_HOMING_OFFSET 800
#define B_HOMING_SPEED 3000
#define B_SHOMING_SPEED 800

// DEF. VALUES FOR BIG MOTOR
#define DEFAULT_SPEED 1000
#define DEF_ACCEL 100000

// DEF. VALUES FOR BIG MOTOR
#define B_DEFAULT_SPEED 1000
#define B_DEF_ACCEL 100000

// VALUES FOR TMC
#define STALL_VALUE 15
#define R_SENSE 0.11f

// WRITE ADDRESS
#define WRITE_ADDR 0x80

int cs_select[] = {8, 2};
TMC2130Stepper driver[] = {TMC2130Stepper(CS1_PIN, R_SENSE), TMC2130Stepper(CS2_PIN, R_SENSE)};
TMC5160Stepper sdriver[] = {TMC5160Stepper(CS3_PIN, R_SENSE), TMC5160Stepper(CS4_PIN, R_SENSE), TMC5160Stepper(CS5_PIN, R_SENSE)};
AccelStepper stepper[] = {
  AccelStepper(1, STEP1_PIN, DIR1_PIN),
  AccelStepper(1, STEP2_PIN, DIR2_PIN),
  AccelStepper(1, STEP3_PIN, DIR3_PIN),
  AccelStepper(1, STEP4_PIN, DIR4_PIN),
  AccelStepper(1, STEP5_PIN, DIR5_PIN)};

// WIFI
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// MOTOR1 ARGUMENTS
float current_deg1 = 0;
float move_to_deg1 = 0;
int move_to1 = 0;
bool home_mot1 = false;
bool second_home1 = false;
bool home_slow1 = false;

// MOTOR2 ARGUMENTS
float current_deg2 = 0;
float move_to_deg2 = 0;
int move_to2 = 0;
bool home_mot2 = false;
bool second_home2 = false;
bool home_slow2 = false;

// MOTOR3 ARGUMENTS
float current_deg3 = 0;
float move_to_deg3 = 0;
int move_to3 = 0;
bool home_mot3 = false;
bool second_home3 = false;
bool home_slow3 = false;

// MOTOR4 ARGUMENTS
float current_deg4 = 0;
float move_to_deg4 = 0;
int move_to4 = 0;
bool home_mot4 = false;
bool second_home4 = false;
bool home_slow4 = false;

// MOTOR5 ARGUMENTS
float current_deg5 = 0;
float move_to_deg5 = 0;
int move_to5 = 0;
bool home_mot5 = false;
bool second_home5 = false;
bool home_slow5 = false;

bool can_move = false;

void initTMC2130(int num, int mcrstps){
  driver[num].begin();                                                                      // Initiate pins and registeries
  driver[num].rms_current(1000, 0.8); // Set stepper current, second parameter is hold_multiplier
  driver[num].en_pwm_mode(1);                                                               // Enable extremely quiet stepping
  driver[num].toff(4);                                                                      // off time
  driver[num].blank_time(24);                                                               // blank tim
  driver[num].pwm_autoscale(1);
  driver[num].microsteps(mcrstps); // What microstep range to use
  driver[num].ihold(18);
  driver[num].irun(18);
  driver[num].TPWMTHRS(20);
}

void initTMC5160(int num, int mcrstps){
  sdriver[num].begin();                                                                      // Initiate pins and registeries
  sdriver[num].rms_current(1000, 0.8); // Set stepper current, second parameter is hold_multiplier
  sdriver[num].en_pwm_mode(1);                                                               // Enable extremely quiet stepping
  sdriver[num].toff(4);                                                                      // off time
  sdriver[num].blank_time(24);                                                               // blank tim
  sdriver[num].pwm_autoscale(1);
  sdriver[num].microsteps(mcrstps); // What microstep range to use
  sdriver[num].ihold(18);
  sdriver[num].irun(18);
  sdriver[num].TPWMTHRS(20);
}

void initStepper(int num){
  stepper[num].setMaxSpeed(100000);
  stepper[num].setAcceleration(100000);
  stepper[num].setSpeed(1000);
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;

  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    String msg = (char*)data;
    Serial.println(msg);
    int str_len = msg.length();
    String cmpr = msg.substring(0, 2);
    switch (cmpr.toInt())
    {
    // START MOVEMENT
    case 0:
      can_move = true;
      break;
    
    // POSITION SET
    case 10:
      move_to_deg1 = msg.substring(2, str_len).toFloat();
      move_to1 = int(ONE_ROTATION / (360 / move_to_deg1));
      stepper[0].moveTo(move_to1);
      current_deg1 = move_to_deg1;
      break;
    case 20:
      move_to_deg2 = msg.substring(2, str_len).toFloat();
      move_to2 = int(ONE_ROTATION / (360 / move_to_deg2));
      stepper[1].moveTo(move_to2);
      current_deg2 = move_to_deg2;
      break;
    case 30:
      move_to_deg3 = msg.substring(2, str_len).toFloat();
      move_to3 = int(B_ONE_ROTATION / (360 / move_to_deg3));
      stepper[2].moveTo(move_to3);
      current_deg3 = move_to_deg3;
      break;
    case 40:
      move_to_deg4 = msg.substring(2, str_len).toFloat();
      move_to4 = int(B_ONE_ROTATION / (360 / move_to_deg4));
      stepper[3].moveTo(move_to4);
      current_deg4 = move_to_deg4;
      break;
    case 50:
      move_to_deg5 = msg.substring(2, str_len).toFloat();
      move_to5 = int(ONE_ROTATION / (360 / move_to_deg5));
      stepper[4].moveTo(move_to5);
      current_deg5 = move_to_deg5;
      break;

    // SET SPEED
    case 11:
      stepper[0].setMaxSpeed(msg.substring(2, str_len).toInt());
      break;
    case 21:
      stepper[1].setMaxSpeed(msg.substring(2, str_len).toInt());
      break;
    case 31:
      stepper[2].setMaxSpeed(msg.substring(2, str_len).toInt());
      break;
    case 41:
      stepper[3].setMaxSpeed(msg.substring(2, str_len).toInt());
      break;
    case 51:
      stepper[4].setMaxSpeed(msg.substring(2, str_len).toInt());
      break;
    
    // SET ACCELERATION
    case 12:
      stepper[0].setAcceleration(msg.substring(2, str_len).toInt());
      break;
    case 22:
      stepper[1].setAcceleration(msg.substring(2, str_len).toInt());
      break;
    case 32:
      stepper[2].setAcceleration(msg.substring(2, str_len).toInt());
      break;
    case 42:
      stepper[3].setAcceleration(msg.substring(2, str_len).toInt());
      break;
    case 52:
      stepper[4].setAcceleration(msg.substring(2, str_len).toInt());
      break;
    
    // HOME MOTOR
    case 13:
      home_mot1 = true;
      stepper[0].setSpeed(-HOMING_SPEED);
      stepper[0].setMaxSpeed(HOMING_SPEED);
      stepper[0].setAcceleration(DEF_ACCEL);
      break;
    case 23:
      home_mot2 = true;
      stepper[1].setSpeed(-HOMING_SPEED);
      stepper[1].setMaxSpeed(HOMING_SPEED);
      stepper[1].setAcceleration(DEF_ACCEL);
      break;
    case 33:
      home_mot3 = true;
      stepper[2].setSpeed(-B_HOMING_SPEED);
      stepper[2].setMaxSpeed(B_HOMING_SPEED);
      stepper[2].setAcceleration(DEF_ACCEL);
      break;
    case 43:
      home_mot4 = true;
      stepper[3].setSpeed(-B_HOMING_SPEED);
      stepper[3].setMaxSpeed(B_HOMING_SPEED);
      stepper[3].setAcceleration(DEF_ACCEL);
      break;
    case 53:
      home_mot5 = true;
      stepper[4].setSpeed(-HOMING_SPEED);
      stepper[4].setMaxSpeed(HOMING_SPEED);
      stepper[4].setAcceleration(DEF_ACCEL);
      break;
    
    // ENABLE MOTORS
    case 19:
      digitalWrite(EN1_PIN, msg.charAt(2) == '1' ? LOW : HIGH);
    case 29:
      digitalWrite(EN2_PIN, msg.charAt(2) == '1' ? LOW : HIGH);
    case 39:
      digitalWrite(EN3_PIN, msg.charAt(2) == '1' ? LOW : HIGH);
    case 49:
      digitalWrite(EN4_PIN, msg.charAt(2) == '1' ? LOW : HIGH);
    case 59:
      digitalWrite(EN5_PIN, msg.charAt(2) == '1' ? LOW : HIGH);
    
    // GIVE CURRENT POSITION
    case 18:
      ws.textAll((String)current_deg1);
      break;
    case 28:
      ws.textAll((String)current_deg2);
      break;
    case 38:
      ws.textAll((String)current_deg3);
      break;
    case 48:
      ws.textAll((String)current_deg4);
      break;
    case 58:
      ws.textAll((String)current_deg5);
      break;
    
    // INITIATE TMCs
    case 99:
      initTMC2130(0, 16);
      initTMC2130(1, 16);
      initTMC5160(0, 8);
      initTMC5160(1, 8);
      initTMC5160(2, 16);
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

  pinMode(SW1_PIN, INPUT_PULLUP);
  pinMode(SW2_PIN, INPUT_PULLUP);
  pinMode(SW3_PIN, INPUT_PULLUP);
  pinMode(SW4_PIN, INPUT_PULLUP);
  pinMode(SW5_PIN, INPUT_PULLUP);
  
  SPI.begin(SCK_PIN, SDO_PIN, SDI_PIN);
  for(int i = 0; i < 5; i++)
  
  digitalWrite(EN1_PIN, HIGH);
  digitalWrite(EN2_PIN, HIGH);
  digitalWrite(EN3_PIN, HIGH);
  digitalWrite(EN4_PIN, HIGH);
  digitalWrite(EN5_PIN, HIGH);
}

void loop() {
  if(can_move){
    for(int i = 0; i < 5; i++){
      stepper[i].run();
    }
    
    bool stop_move = true;
    for(int i = 0; i < 5; i++){
      stop_move = stop_move && (stepper[i].distanceToGo() == 0);
    }
    can_move = !stop_move;

  }
  
  if(home_mot1){
    if(second_home1) {
      if (stepper[0].distanceToGo() == 0){
        second_home1 = false;
        stepper[0].setSpeed(-SHOMING_SPEED);
      } else {
        stepper[0].run();
      }
    } else if(digitalRead(SW1_PIN) == 1) {
        stepper[0].runSpeed();
    } else {
      if(home_slow1){
        home_mot1 = false;
        home_slow1 = false;
        current_deg1 = 0;
        stepper[0].setCurrentPosition(0);
      } else {
        home_slow1 = true;
        second_home1 = true;
        stepper[0].setCurrentPosition(0);
        stepper[0].moveTo(HOMING_OFFSET);
      }
    }
  }

  if(home_mot2){
    if(second_home2) {
      if (stepper[1].distanceToGo() == 0){
        second_home2 = false;
        stepper[1].setSpeed(-SHOMING_SPEED);
      } else {
        stepper[1].run();
      }
    } else if(digitalRead(SW2_PIN) == 1) {
        stepper[1].runSpeed();
    } else {
      if(home_slow2){
        home_mot2 = false;
        home_slow2 = false;
        current_deg2 = 0;
        stepper[1].setCurrentPosition(0);
      } else {
        home_slow2 = true;
        second_home2 = true;
        stepper[1].setCurrentPosition(0);
        stepper[1].moveTo(HOMING_OFFSET);
      }
    }
  }

  if(home_mot3){
    if(second_home3) {
      if (stepper[2].distanceToGo() == 0){
        second_home3 = false;
        stepper[2].setSpeed(-B_SHOMING_SPEED);
      } else {
        stepper[2].run();
      }
    } else if(digitalRead(SW3_PIN) == 1) {
        stepper[2].runSpeed();
    } else {
      if(home_slow3){
        home_mot3 = false;
        home_slow3 = false;
        current_deg3 = 0;
        stepper[2].setCurrentPosition(0);
      } else {
        home_slow3 = true;
        second_home3 = true;
        stepper[2].setCurrentPosition(0);
        stepper[2].moveTo(B_HOMING_OFFSET);
      }
    }
  }

  if(home_mot4){
    if(second_home4) {
      if (stepper[3].distanceToGo() == 0){
        second_home4 = false;
        stepper[3].setSpeed(-B_SHOMING_SPEED);
      } else {
        stepper[3].run();
      }
    } else if(digitalRead(SW4_PIN) == 1) {
        stepper[3].runSpeed();
    } else {
      if(home_slow4){
        home_mot4 = false;
        home_slow4 = false;
        current_deg4 = 0;
        stepper[3].setCurrentPosition(0);
      } else {
        home_slow4 = true;
        second_home4 = true;
        stepper[3].setCurrentPosition(0);
        stepper[3].moveTo(B_HOMING_OFFSET);
      }
    }
  }

  if(home_mot5){
    if(second_home5) {
      if (stepper[4].distanceToGo() == 0){
        second_home5 = false;
        stepper[4].setSpeed(-B_SHOMING_SPEED);
      } else {
        stepper[4].run();
      }
    } else if(digitalRead(SW5_PIN) == 1) {
        stepper[4].runSpeed();
    } else {
      if(home_slow5){
        home_mot5 = false;
        home_slow5 = false;
        current_deg5 = 0;
        stepper[4].setCurrentPosition(0);
      } else {
        home_slow5 = true;
        second_home5 = true;
        stepper[4].setCurrentPosition(0);
        stepper[4].moveTo(HOMING_OFFSET);
      }
    }
  }
}