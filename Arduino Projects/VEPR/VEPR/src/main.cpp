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
#include "joint.h"
#include "constants.h"

using namespace std;
using namespace TMC2130_n;

bool can_move = false;
int default_steps = 200;

MotorJoint joints[] = {
    MotorJoint(STEP0_PIN, DIR0_PIN, CS0_PIN, EN0_PIN, R_SENSE),
    MotorJoint(STEP1_PIN, DIR1_PIN, CS1_PIN, EN1_PIN, R_SENSE),
    MotorJoint(STEP2_PIN, DIR2_PIN, CS2_PIN, EN2_PIN, R_SENSE),
    MotorJoint(STEP3_PIN, DIR3_PIN, CS3_PIN, EN3_PIN, R_SENSE),
    MotorJoint(STEP4_PIN, DIR4_PIN, CS4_PIN, EN4_PIN, R_SENSE),
    MotorJoint(STEP5_PIN, DIR5_PIN, CS5_PIN, EN5_PIN, R_SENSE),
};

// WIFI
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

void actionSwitcher(int mot, String msg){
  int str_len = msg.length();
  String act = msg.substring(1, 3);
  Serial.println((String)mot + " action: " + act + ", " + msg.substring(3, str_len));
  switch (act.toInt()){
    case 00: //Enable motor
        joints[mot].EnableMotor(msg.charAt(3) == '1' ? HIGH : LOW);
        break;
    case 01:
        joints[mot].SetTravel(msg.substring(3, str_len).toFloat());
    case 02: //Set speed
        joints[mot].mot_speed = msg.substring(3, str_len).toInt();
        Serial.println("Changed speed of " + (String)mot + ", " + (String)joints[mot].mot_speed);
        break;
    case 03: //Set acceleration
        joints[mot].mot_accel = msg.substring(3, str_len).toInt();
        Serial.println("Changed acceleration of " + (String)mot + ", " + (String)joints[mot].mot_accel);
        break;
    case 04: //Set reduction
        joints[mot].mot_reduction = msg.substring(3, str_len).toFloat();
        Serial.println("Changed reduction of " + (String)mot + ", " + (String)joints[mot].mot_reduction);
        break;
    case 11: //Set homing speed
        joints[mot].mot_home_speed = msg.substring(3, str_len).toInt();
        break;
    case 12: //Set inverse homing
        joints[mot].mot_home_inv = msg.charAt(3) == '1' ? true : false;
        break;
    case 13: //Set homing acceleration
        joints[mot].mot_home_accel = msg.substring(3, str_len).toInt();
        break;
    case 14: //Set homing offset
        joints[mot].mot_shome_offset = msg.substring(3, str_len).toInt();
        break;
    case 15: //Set second homing speed mult
        joints[mot].mot_home_mult = msg.substring(3, str_len).toFloat();
    case 16://Set homing offset
        joints[mot].mot_home_offset = msg.substring(3, str_len).toFloat();
        break;
    case 20: //Initiate TMC Driver
        joints[mot].InitTMC();
        break;
    case 21: //Set Microsteps
        joints[mot].mot_mcrs = msg.substring(3, str_len).toInt();
        break;
    case 22: //Set IRUN
        joints[mot].mot_irun = msg.substring(3, str_len).toInt();
        break;
    case 23: //Set IHOLD
        joints[mot].mot_ihold = msg.substring(3, str_len).toFloat();
        break;
    case 80: //Give current position
        ws.textAll((String)joints[mot].GetCurrentPosition());
        break;
    case 81:
        Serial.println((String)mot + " Set new current position " +  (String)msg.substring(3, str_len).toFloat() + " With Steps " + (String)int((default_steps * joints[mot].mot_reduction * joints[mot].mot_mcrs) * (msg.substring(3, str_len).toFloat() / 360)));
        joints[mot].stepper.setCurrentPosition(int((default_steps * joints[mot].mot_reduction * joints[mot].mot_mcrs) * (msg.substring(3, str_len).toFloat() / 360)));
        break;
  }
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;

  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    String msg = (char*)data;
    int str_len = msg.length();
    String mot = msg.substring(0, 1);
    String act = msg.substring(1, 3);
    Serial.println((String)mot + "act : " + (String)act);
    switch (mot.toInt()){
        case 0:
            actionSwitcher(0, msg);
            break;
        case 1:
            actionSwitcher(1, msg);
            break;
        case 2:
            actionSwitcher(2, msg);
            break;
        case 3:
            actionSwitcher(3, msg);
            break;
        case 4:
            actionSwitcher(4, msg);
            break;
        case 5:
            actionSwitcher(5, msg);
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
        Serial.println("Received Message");
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

void setup(){
    Serial.begin(115200);

    Serial.println("ESP32 is ready!");

    WiFi.mode(WIFI_AP);
    WiFi.softAP("ESP32AAA", "12345678");

    IPAddress IP = WiFi.softAPIP();
    Serial.println("AP IP adress: ");
    Serial.print(IP);

    initWebSocket();

    server.begin();

    pinMode(EN0_PIN, OUTPUT);
    pinMode(EN1_PIN, OUTPUT);
    pinMode(EN2_PIN, OUTPUT);
    pinMode(EN3_PIN, OUTPUT);
    pinMode(EN4_PIN, OUTPUT);
    pinMode(EN5_PIN, OUTPUT);

    for (int i = 0; i < 6; i++){
        joints[i].EnableMotor(0);
    }

    pinMode(SW0_PIN, INPUT_PULLUP);
    pinMode(SW1_PIN, INPUT_PULLUP);
    pinMode(SW2_PIN, INPUT_PULLUP);
    pinMode(SW3_PIN, INPUT_PULLUP);
    pinMode(SW4_PIN, INPUT_PULLUP);
    pinMode(SW5_PIN, INPUT_PULLUP);

    SPI.begin(SCK_PIN, SDO_PIN, SDI_PIN);
}

void loop(){
    if (can_move){
        for(int i = 0; i < 6; i++){
            joints[i].stepper.run();
        }
        bool stop_move = true;
        for(int i = 0; i < 6; i++){
            if (!joints[i].IsFinished()){
                stop_move = false;
                break;
            } 
        }
        can_move = !stop_move;
        if (stop_move) Serial.println("STOPPED");
    }
}