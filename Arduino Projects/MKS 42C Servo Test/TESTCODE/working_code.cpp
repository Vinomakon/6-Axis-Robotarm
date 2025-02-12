#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <map>
#include <bitset>
#include <vector>
#include <math.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>

using namespace std;

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
#define ONE_ROTATION 3200
#define HOME_OFFSET 400
#define DEFAULT_SPEED 1000
#define HOMING_SPEED 1000
#define SHOMING_SPEED 200

// VALUES FOR TMC
#define STALL_VALUE 15
#define R_SENSE 0.11f
#define MSTEP 256

// WRITE ADDRESS
#define WRITE_ADDR 0x80


float steps_per_sec = 500;
int steps_mils = int(1000000 / steps_per_sec);

// WIFI
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// MOTOR1 ARGUMENTS
float current_deg1 = 0;
int current_pos1 = 0;
float move_to_deg1 = 0;
int move_to1 = 0;
bool pos_movement1 = true;
float sps1 = 1000;
int sps_mic1 = int(1000000 / sps1);
bool home_mot1 = false;
bool second_home1 = false;
bool home_slow1 = false;

// MOTOR2 ARGUMENTS
float current_deg2 = 0;
int current_pos2 = 0;
float move_to_deg2 = 0;
int move_to2 = 0;
bool pos_movement2 = true;
float sps2 = 1000;
int sps_mic2 = int(1000000 / sps2);
bool home_mot2 = false;
bool second_home2 = false;
bool home_slow2 = false;

bool can_move = false;

class ChopConfig{
  public:
    int config_adr = 0x6C;

    bitset<40> getWriteBitset(){
      long long int msg = 0;
      for(int i = 0; i < config.size(); i++){
          if(config[config.size() - 1 - i]){
            msg += pow(2, i);
          }
      }
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    vector<bool> config ={
      false, //diss2g
      false, //dedge
      false, //intpol
      false, //mres3
      true, //mres2
      false, //mres1
      false, //mres0
      false, //sync3
      false, //sync2
      false, //sync1
      false, //sync0
      false, //vhighchm
      false, //vhighfs
      false, //vsense
      false, //tbl1
      true, //tbl0
      false, //chm
      false, //rndtf
      false, //disfdcc
      false, //fd3
      false, //hend3
      false, //hend2
      false, //hend1
      false, //hend0
      false, //hstrt2
      false, //hstrt1
      false, //hstrt0
      false, //toff3
      true, //toff2
      false, //toff1
      false //toff0
    };
};

class GConf{
  public:
    int config_adr = 0x00;
    
    bitset<40> getWriteBitset(){
      long long int msg = 0;
      for(int i = 0; i < config.size(); i++){
          if(config[config.size() - 1 -i]){
            msg += pow(2, i);
          }
      }
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    vector<bool> config ={
      false, //test_mode
      false, //direct_mode
      false, //stop_enable
      false, //small_hysteresis
      false, //diag1_pushpull
      false, //diag0_int_pushpull
      false, //diag1_steps_skipped
      false, //diag1_onstate
      false, //diag1_index
      false, //diag1_stall
      false, //diag0_stall
      false, //diag0_otpw
      false, //diag0_error
      false, //shaft
      false, //enc_commutation
      true, //en_pwm_mode
      false, //internal_Rsense
      false  //I_scale_analog
    };
};

class PWMConfig{
  public:
    int config_adr = 0x70;
    
    bitset<40> getWriteBitset(){
      long long int msg = 0;
      for(int i = 0; i < config.size(); i++){
          if(config[config.size() - 1 -i]){
            msg += pow(2, i);
          }
      }
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    vector<bool> config ={
      false, //freewheel1
      false, //freewheel0
      false, //pwm_symmetric
      true, //pwm_autoscale
      false, //pwm_freq1
      false, //pwm_freq0
      false, //PWM_GRAD 7
      false, //PWM_GRAD 6
      false, //PWM_GRAD 5
      false, //PWM_GRAD 4
      false, //PWM_GRAD 3
      false, //PWM_GRAD 2
      false, //PWM_GRAD 1
      false, //PWM_GRAD 0
      false, //PWM_AMPL 7
      false, //PWM_AMPL 6
      false, //PWM_AMPL 5
      false, //PWM_AMPL 4
      false, //PWM_AMPL 3
      false, //PWM_AMPL 2
      false, //PWM_AMPL 1
      false  //PWM_AMPL 0
    };
};

class CoolConfig{
  public:
    int config_adr = 0x6D;
    
    bitset<40> getWriteBitset(){
      long long int msg = 0;
      for(int i = 0; i < config.size(); i++){
          if(config[config.size() - 1 -i]){
            msg += pow(2, i);
          }
      }
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    vector<bool> config ={
      true, //sfilt
      false, 
      false, //sgt6
      false, //sgt5
      false, //sgt4
      false, //sgt3
      false, //sgt2
      false, //sgt1
      false, //sgt0
      false, //seimin
      false, //sedn1
      true, //sedn0
      false, 
      false, //semax3
      false, //semax2
      true, //semax1
      false, //semax0
      false, 
      false, //seup1
      false, //seup0
      false, 
      false, //semin3
      true, //semin2
      false, //semin1
      true  //semin0
    };
};

class IHold_IRun{
  public:
    int config_adr = 0x10;

    bitset<40> getWriteBitset(){
      long long int msg = 0;
      msg += IHOLD - 1 + 
      pow(2, 8) * (IRUN - 1) + 
      pow(2, 16) * (IRUN - 1);
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    int IHOLD = 20; //1-32
    int IRUN = 20; //1-32
    int IHOLDDELAY = 0; //1-16
};

class TPowerdown{
  public:
    int config_adr = 0x11;

    bitset<40> getWriteBitset(){
      long long int msg = 0; 
      msg += TPOWERDOWN;
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    int TPOWERDOWN = 0; //0-255
};

class TPWMThreshold{
  public:
    int config_adr = 0x13;

    bitset<40> getWriteBitset(){
      long long int msg = 0; 
      msg += TPWMTHRS;
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    int TPWMTHRS = 20; //0-1'048'576
};

class TCoolThreshold{
  public:
    int config_adr = 0x14;

    bitset<40> getWriteBitset(){
      long long int msg = 0; 
      msg += TCOOLTHRS;
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    int TCOOLTHRS = 0xFFFFF; //0-1'048'576
};

class THigh{
  public:
    int config_adr = 0x15;

    bitset<40> getWriteBitset(){
      long long int msg = 0; 
      msg += THIGH;
      msg += pow(2, 32) * (config_adr + WRITE_ADDR);
      return bitset<40>(msg);
    }

    int THIGH = 0; //0-1'048'576
};

ChopConfig chopconfig;
GConf gconf;
IHold_IRun ihold_irun;
TPowerdown tpowerdown;
TPWMThreshold tpwmthreshold;
PWMConfig pwmconfig;
CoolConfig coolconfig;
TCoolThreshold tcoolthreshold;
THigh thigh;

bitset<40> CHOPCONFIG = chopconfig.getWriteBitset();
bitset<40> IHOLD_IRUN = ihold_irun.getWriteBitset();
bitset<40> TPOWERDOWN = tpowerdown.getWriteBitset();
bitset<40> GCONF = gconf.getWriteBitset();
bitset<40> TPWM_THRS = tpwmthreshold.getWriteBitset();
bitset<40> PWMCONF = pwmconfig.getWriteBitset();
bitset<40> COOLCONFIG = coolconfig.getWriteBitset();
bitset<40> TCOOLTHRS = tcoolthreshold.getWriteBitset();
bitset<40> THIGH = thigh.getWriteBitset();

void tData(bitset<40> data){
  string b_data = data.to_string();
  
  for (int i = 0; i < 40; i++){
    if (b_data[i] == '1'){
      delayMicroseconds(1);
      digitalWrite(SDI_PIN, HIGH);
    } else{
    }
    delayMicroseconds(1);
    digitalWrite(SCK_PIN, HIGH);
    delayMicroseconds(1);
    digitalWrite(SCK_PIN, LOW);
    delayMicroseconds(1);
    digitalWrite(SDI_PIN, LOW);
  }
}

void ack(int CS_PIN){
  delayMicroseconds(1);
  digitalWrite(CS_PIN, HIGH);
  delayMicroseconds(1);
  digitalWrite(SCK_PIN, HIGH);
  delayMicroseconds(1);
  digitalWrite(CS_PIN, LOW);
  delayMicroseconds(1);
  digitalWrite(SCK_PIN, LOW);
}

void readTMC(){
  bitset<8> data(0x6F);
  string b_data = data.to_string();
  for (int i = 0; i < 8; i++){
    if (b_data[i] == '1'){
      delayMicroseconds(1);
      digitalWrite(SDI_PIN, HIGH);
    }
    delayMicroseconds(1);
    digitalWrite(SCK_PIN, HIGH);
    delayMicroseconds(1);
    digitalWrite(SCK_PIN, LOW);
    delayMicroseconds(1);
    digitalWrite(SDI_PIN, LOW);
  }
  String in_data = "";
  for (int i = 0; i < 32; i++){
    digitalWrite(SCK_PIN, HIGH);
    if (digitalRead(SDO_PIN)){
      in_data += "1";
    } else{
      in_data += "0";
    }
  }
}

void initTMC(int CS){
  //Start Seq.
  ack(CS);
  //Init Data
  tData(CHOPCONFIG);
  ack(CS);
  tData(IHOLD_IRUN);
  ack(CS);
  //tData(TPOWERDOWN);
  //ack(CS);
  //tData(GCONF);
  //ack(CS);
  //tData(TPWM_THRS);
  //ack(CS);
  //tData(PWMCONF);
  //ack(CS);
  tData(THIGH);
  ack(CS);
  tData(TCOOLTHRS);
  ack(CS);
  tData(COOLCONFIG);
  ack(CS);
  readTMC();
  digitalWrite(SCK_PIN, LOW);
  digitalWrite(SDI_PIN, LOW);
  digitalWrite(CS, HIGH);
  Serial.println("ESP32 has communicated!");
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
      Serial.println("Invoked Motor Start");
      break;
    case 10:
      move_to_deg1 = msg.substring(2, str_len).toFloat();
      move_to1 = int(ONE_ROTATION / (360 / move_to_deg1));;
      pos_movement1 = 0 < move_to1 - current_pos1;
      digitalWrite(DIR1_PIN, pos_movement1);
      Serial.println("Invoked first motor");
      Serial.println(msg.substring(2, str_len));
      Serial.println(move_to_deg1);
      break;
    case 20:
      move_to_deg2 = msg.substring(2, str_len).toFloat();
      move_to2 = int(ONE_ROTATION / (360 / move_to_deg2));;
      pos_movement2 = 0 < move_to2 - current_pos2;
      digitalWrite(DIR2_PIN, pos_movement2);
      Serial.println("Invoked second motor");
      Serial.println(msg.substring(2, str_len));
      Serial.println(move_to_deg2);
      break;
    case 11:
      sps1 = msg.substring(2, str_len).toFloat();
      sps_mic1 = int(1000000 / sps1);
      break;
    case 21:
      sps2 = msg.substring(2, str_len).toFloat();
      sps_mic2 = int(1000000 / sps2);
      break;
    case 13:
      home_mot1 = true;
      sps1 = HOMING_SPEED;
      sps_mic1 = int(1000000 / sps1);
      digitalWrite(DIR1_PIN, LOW);
      break;
    case 23:
      home_mot2 = true;
      sps2 = HOMING_SPEED;
      sps_mic2 = int(1000000 / sps2);
      digitalWrite(DIR2_PIN, LOW);
      break;
    case 18:
      ws.textAll((String)current_deg1);
      break;
    case 28:
      ws.textAll((String)current_deg2);
      break;
    case 1:
      sps1 = msg.substring(2, str_len).toFloat();
      sps_mic1 = int(1000000 / sps1);
      sps2 = msg.substring(2, str_len).toFloat();
      sps_mic2 = int(1000000 / sps2);
      break;
    case 99:
      initTMC(CS1_PIN);
      initTMC(CS2_PIN);
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

  pinMode(DIR1_PIN, OUTPUT);
  pinMode(STEP1_PIN, OUTPUT);
  pinMode(EN1_PIN, OUTPUT);
  pinMode(CS1_PIN, OUTPUT);
  pinMode(SW1_PIN, INPUT_PULLUP);

  pinMode(DIR2_PIN, OUTPUT);
  pinMode(STEP2_PIN, OUTPUT);
  pinMode(EN2_PIN, OUTPUT);
  pinMode(CS2_PIN, OUTPUT);
  pinMode(SW2_PIN, INPUT_PULLUP);

  pinMode(SCK_PIN, OUTPUT);
  pinMode(SDI_PIN, OUTPUT);
  pinMode(SDO_PIN, INPUT_PULLUP);
  

  digitalWrite(EN1_PIN, LOW);
  digitalWrite(DIR1_PIN, LOW);

  digitalWrite(EN2_PIN, LOW);
  digitalWrite(DIR2_PIN, LOW);

  digitalWrite(CS1_PIN, LOW);
  digitalWrite(CS2_PIN, LOW);
}

/*
void moveTo(float move_deg){
  int move_pos = int(ONE_ROTATION / (360 / move_deg));
  int total_move = move_pos - current_pos1;
  if(total_move < 0){
    digitalWrite(DIR1_PIN, HIGH);
  } else{
    digitalWrite(DIR1_PIN, LOW);
  }

  for(int i = 0; i < abs(total_move); i++){
    delayMicroseconds(int(1000 * steps_mils / 2));
    digitalWrite(STEP1_PIN, HIGH);
    delayMicroseconds(int(1000 * steps_mils / 2));
    digitalWrite(STEP1_PIN, LOW);
  }

  current_deg = move_deg;
  current_pos = move_pos;
}*/

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
    if ((us - mot1_last) >= sps_mic1 && (pos_movement1 ? current_pos1 < move_to1 : current_pos1 > move_to1)){
      current_pos1 += pos_movement1 ? 1 : -1;
      mot1_last = us;
      digitalWrite(STEP1_PIN, HIGH);
      digitalWrite(STEP1_PIN, LOW);
    }
    if ((us - mot2_last) >= sps_mic2 && (pos_movement2 ? current_pos2 < move_to2 : current_pos2 > move_to2)){
      current_pos2 += pos_movement2 ? 1 : -1;
      mot2_last = us;
      digitalWrite(STEP2_PIN, HIGH);
      digitalWrite(STEP2_PIN, LOW);
    }

    if(current_pos1 == move_to1 && current_pos2 == move_to2){
      can_move = false;
    }
  } else {
    if (current_pos1 == move_to1) {
      current_deg1 = move_to_deg1;
    }
    if (current_pos2 == move_to2) {
      current_deg2 = move_to_deg2;
    }
  }
  
  if(home_mot1){
    if(second_home1) {
      if (current_pos1 >= move_to1){
        digitalWrite(DIR1_PIN, LOW);
        second_home1 = false;
        sps1 = SHOMING_SPEED;
        sps_mic1 = int(1000000 / sps1);
      } else if ((us - mot1_last) >= sps_mic1){
        current_pos1++;
        mot1_last = us;
        digitalWrite(STEP1_PIN, HIGH);
        digitalWrite(STEP1_PIN, LOW);
      }
    } else if(digitalRead(SW1_PIN) == 1) {
        if ((us - mot1_last) >= sps_mic1){
          mot1_last = us;
          digitalWrite(STEP1_PIN, HIGH);
          digitalWrite(STEP1_PIN, LOW);
        }
    } else {
      if(home_slow1){
        home_mot1 = false;
        home_slow1 = false;
        current_pos1 = 0;
        current_deg1 = 0;
      } else {
        home_slow1 = true;
        second_home1 = true;
        current_pos1 = 0;
        move_to1 = HOME_OFFSET;
        digitalWrite(DIR1_PIN, HIGH);
      }
    }
  }

  if(home_mot2){
    if(second_home2) {
      if (current_pos2 >= move_to2){
        digitalWrite(DIR2_PIN, LOW);
        second_home2 = false;
        sps2 = SHOMING_SPEED;
        sps_mic2 = int(1000000 / sps2);
      } else if ((us - mot2_last) >= sps_mic2){
        current_pos2++;
        mot2_last = us;
        digitalWrite(STEP2_PIN, HIGH);
        digitalWrite(STEP2_PIN, LOW);
      }
    } else if(digitalRead(SW2_PIN) == 1) {
        if ((us - mot2_last) >= sps_mic2){
          mot2_last = us;
          digitalWrite(STEP2_PIN, HIGH);
          digitalWrite(STEP2_PIN, LOW);
        }
    } else {
      if(home_slow2){
        home_mot2 = false;
        home_slow2 = false;
        current_pos2 = 0;
        current_deg2 = 0;
      } else {
        home_slow2 = true;
        second_home2 = true;
        current_pos2 = 0;
        move_to2 = HOME_OFFSET;
        digitalWrite(DIR2_PIN, HIGH);
      }
    }
  }
}