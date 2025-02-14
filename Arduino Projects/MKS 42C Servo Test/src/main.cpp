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

// PINS FOR MOTOR 1
#define DIR2_PIN 4
#define STEP2_PIN 3
#define EN2_PIN 1
#define CS2_PIN 2
#define SW2_PIN 46

// VALUES FOR ESP
#define DEFAULT_MRES 16
#define ONE_ROTATION 200 * DEFAULT_MRES

#define HOMING_OFFSET 400
#define HOMING_SPEED 1000
#define SHOMING_SPEED 200

#define DEFAULT_SPEED 1000
#define DEF_ACCEL 100000

// VALUES FOR TMC
#define STALL_VALUE 15
#define R_SENSE 0.11f
#define MSTEP 256

// WRITE ADDRESS
#define WRITE_ADDR 0x80

int cs_select[] = {8, 2};
TMC2130Stepper driver[] = {TMC2130Stepper(CS1_PIN, R_SENSE), TMC2130Stepper(CS2_PIN, R_SENSE)};
AccelStepper stepper[] = {AccelStepper(1, STEP1_PIN, DIR1_PIN), AccelStepper(1, STEP2_PIN, DIR2_PIN)};

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

bool can_move = false;

void initTMC(int num){
  driver[num].begin();                                                                      // Initiate pins and registeries
  driver[num].rms_current(1000, 0.8); // Set stepper current, second parameter is hold_multiplier
  driver[num].en_pwm_mode(1);                                                               // Enable extremely quiet stepping
  driver[num].toff(4);                                                                      // off time
  driver[num].blank_time(24);                                                               // blank tim
  driver[num].pwm_autoscale(1);
  driver[num].microsteps(DEFAULT_MRES); // What microstep range to use
  driver[num].ihold(18);
  driver[num].irun(18);
  driver[num].TPWMTHRS(20);
}

void initStepper(int num){
  stepper[num].setMaxSpeed(1000);
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
    case 0:
      can_move = true;
      break;
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
    case 11:
      stepper[0].setMaxSpeed(msg.substring(2, str_len).toInt());
      break;
    case 21:
      stepper[1].setMaxSpeed(msg.substring(2, str_len).toInt());
      break;
    case 12:
      stepper[0].setAcceleration(msg.substring(2, str_len).toInt());
      break;
    case 22:
      stepper[1].setAcceleration(msg.substring(2, str_len).toInt());
      break;
    case 13:
      home_mot1 = true;
      stepper[0].setSpeed(-HOMING_SPEED);
      stepper[0].setMaxSpeed(HOMING_SPEED);
      stepper[0].setAcceleration(DEF_ACCEL);
      driver[0].microsteps(DEFAULT_MRES);
      break;
    case 23:
      home_mot2 = true;
      stepper[1].setSpeed(-HOMING_SPEED);
      stepper[1].setMaxSpeed(HOMING_SPEED);
      stepper[1].setAcceleration(DEF_ACCEL);
      driver[1].microsteps(DEFAULT_MRES);
      break;
    case 18:
      ws.textAll((String)current_deg1);
      break;
    case 28:
      ws.textAll((String)current_deg2);
      break;
    case 1:
      stepper[0].setMaxSpeed(msg.substring(2, str_len).toInt());
      stepper[1].setMaxSpeed(msg.substring(2, str_len).toInt());
      break;
    case 99:
      initTMC(0);
      initTMC(1);
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
  pinMode(SW1_PIN, INPUT_PULLUP);

  pinMode(EN2_PIN, OUTPUT);
  pinMode(SW2_PIN, INPUT_PULLUP);
  
  SPI.begin(SCK_PIN, SDO_PIN, SDI_PIN);
  for(int i = 0; i < 2; i++){
    initStepper(i);
  }
  
  digitalWrite(EN1_PIN, LOW);

  digitalWrite(EN2_PIN, LOW);
}

bool sw1_on = false;
int last_sw1 = 0;
bool sw2_on = false;
int last_sw2 = 0;

#define SWITCH_ON_TIME 10000

void loop() {
  static int mot1_last = 0;
  static int mot2_last = 0;

  static bool sw1_on = false;
  static bool sw2_on = false;

  int us = micros();

  if(can_move){
    for(int i = 0; i < 2; i++){
      stepper[i].run();
    }
    
    bool stop_move = true;
    for(int i = 0; i < 2; i++){
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
}