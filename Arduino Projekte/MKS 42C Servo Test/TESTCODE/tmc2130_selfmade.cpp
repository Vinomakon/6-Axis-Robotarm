#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <map>
#include <bitset>
#include <vector>
#include <math.h>

using namespace std;

//PINS FOR TMC
#define DIR_PIN 46
#define STEP_PIN 3
#define SDO_PIN 18
#define CS_PIN 17
#define SCK_PIN 16
#define SDI_PIN 15
#define EN_PIN 7

//VALUES FOR ESP
#define MAX_SPEED 40
#define MIN_SPEED 1000
#define ONE_ROTATION 3200

//VALUES FOR TMC
#define STALL_VALUE 15
#define R_SENSE 0.11f
#define MSTEP 256

#define WRITE_ADDR 0x80

float steps_per_sec = 100;
int steps_mils = int(1000 / steps_per_sec);

String receivedMessage = "";

float current_deg = 0;
int current_pos = 0;

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
      true, //mres1
      true, //mres0
      false, //sync3
      false, //sync2
      false, //sync1
      false, //sync0
      false, //vhighchm
      false, //vhighfs
      false, //vsense
      true, //tbl1
      false, //tbl0
      true, //chm
      true, //rndtf
      true, //disfdcc
      false, //fd3
      false, //hend3
      false, //hend2
      false, //hend1
      true, //hend0
      true, //hstrt2
      false, //hstrt1
      false, //hstrt0
      false, //toff3
      false, //toff2
      false, //toff1
      true //toff0
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
      true, //PWM_AMPL 7
      true, //PWM_AMPL 6
      false, //PWM_AMPL 5
      false, //PWM_AMPL 4
      true, //PWM_AMPL 3
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
      false, //sfilt
      false, //EMPTY
      false, //sgt6
      true, //sgt5
      false, //sgt4
      false, //sgt3
      false, //sgt2
      false, //sgt1
      false, //sgt0
      false, //seimin
      false, //sedn1
      false, //sedn0
      false, //EMPTY
      false, //semax3
      true, //sema2
      true, //semax1
      false, //semax0
      false, //EMPTY
      true, //seup1
      false, //seup0
      false, //EMPTY
      false, //semin3
      false, //semin2
      false, //semin1
      false  //semin0
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

    int IHOLD = 16; //1-32
    int IRUN = 32; //1-32
    int IHOLDDELAY = 16; //1-16
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

class TPWMThreshhold{
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

ChopConfig chopconfig;
GConf gconf;
IHold_IRun ihold_irun;
TPowerdown tpowerdown;
TPWMThreshhold tpwmthreshold;
PWMConfig pwmconfig;

bitset<40> CHOPCONFIG = chopconfig.getWriteBitset();
bitset<40> IHOLD_IRUN = ihold_irun.getWriteBitset();
bitset<40> TPOWERDOWN = tpowerdown.getWriteBitset();
bitset<40> GCONF = gconf.getWriteBitset();
bitset<40> TPWM_THRS = tpwmthreshold.getWriteBitset();
bitset<40> PWMCONF = pwmconfig.getWriteBitset();

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

void ack(){
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

void initTMC(){
  //Start Seq.
  ack();

  //Init Data
  tData(CHOPCONFIG);
  ack();
  tData(IHOLD_IRUN);
  ack();
  //tData(TPOWERDOWN);
  //ack();
  tData(GCONF);
  ack();
  //tData(TPWM_THRS);
  //ack();
  tData(PWMCONF);
  ack();
  //readTMC();
  Serial.println("ESP32 has communicated!");
}

void setup() {
  Serial.begin(115200);

  Serial.println("ESP32 is ready!");

  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);
  pinMode(SCK_PIN, OUTPUT);
  pinMode(SDI_PIN, OUTPUT);
  pinMode(SDO_PIN, INPUT_PULLUP);
  pinMode(CS_PIN, OUTPUT);

  digitalWrite(EN_PIN, LOW);
  digitalWrite(DIR_PIN, LOW);
  digitalWrite(CS_PIN, LOW);

  initTMC();
  digitalWrite(SCK_PIN, LOW);
  digitalWrite(SDI_PIN, LOW);
  digitalWrite(CS_PIN, HIGH);
}

void moveTo(float move_deg){
  int move_pos = int(ONE_ROTATION / (360 / move_deg));
  int total_move = move_pos - current_pos;
  if(total_move < 0){
    digitalWrite(DIR_PIN, HIGH);
  } else{
    digitalWrite(DIR_PIN, LOW);
  }

  for(int i = 0; i < abs(total_move); i++){
    delayMicroseconds(int(1000 * steps_mils / 2));
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(int(1000 * steps_mils / 2));
    digitalWrite(STEP_PIN, LOW);
  }

  current_deg = move_deg;
  current_pos = move_pos;
}

void loop() {
  
  delayMicroseconds(int(1000 * steps_mils / 2));
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(int(1000 * steps_mils / 2));
  digitalWrite(STEP_PIN, LOW);

  // put your main code here, to run repeatedly:
}