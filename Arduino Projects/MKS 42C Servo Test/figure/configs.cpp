#include <bitset>
#include <vector>
#include "configs.h"
#include <math.h>

#define WRITE_ADDR 0x80

bitset<40> ChopConfig::getWriteBitset(){
    long long int msg = 0;
    for(int i = 0; i < ChopConfig::config.size(); i++){
        if(ChopConfig::config[ChopConfig::config.size() - 1 - i]){
          msg += pow(2, i);
        }
    }
    msg += pow(2, 32) * (ChopConfig::config_adr + WRITE_ADDR);
    return bitset<40>(msg);
}
vector<bool> ChopConfig::config = {
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

bitset<40> GConfig::getWriteBitset(){
    long long int msg = 0;
    for(int i = 0; i < GConfig::config.size(); i++){
        if(GConfig::config[GConfig::config.size() - 1 -i]){
          msg += pow(2, i);
        }
    }
    msg += pow(2, 32) * (GConfig::config_adr + WRITE_ADDR);
    return bitset<40>(msg);
}
vector<bool> GConfig::config = {
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

bitset<40> PWMConfig::getWriteBitset(){
    long long int msg = 0;
    for(int i = 0; i < PWMConfig::config.size(); i++){
        if(PWMConfig::config[PWMConfig::config.size() - 1 -i]){
          msg += pow(2, i);
        }
    }
    msg += pow(2, 32) * (PWMConfig::config_adr + WRITE_ADDR);
    return bitset<40>(msg);
}
vector<bool> PWMConfig::config = {
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

bitset<40> CoolConfig::getWriteBitset(){
    long long int msg = 0;
    for(int i = 0; i < CoolConfig::config.size(); i++){
        if(CoolConfig::config[CoolConfig::config.size() - 1 -i]){
          msg += pow(2, i);
        }
    }
    msg += pow(2, 32) * (CoolConfig::config_adr + WRITE_ADDR);
    return bitset<40>(msg);
}
vector<bool> CoolConfig::config = {
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

bitset<40> IHold_IRun::getWriteBitset(){
    long long int msg = 0;
    msg += IHold_IRun::IHOLD - 1 + 
    pow(2, 8) * (IHold_IRun::IRUN - 1) + 
    pow(2, 16) * (IHold_IRun::IHOLDDELAY - 1);
    msg += pow(2, 32) * (config_adr + WRITE_ADDR);
    return bitset<40>(msg);
  }

bitset<40> TPowerdown::getWriteBitset(){
    long long int msg = 0; 
    msg += TPowerdown::TPOWERDOWN;
    msg += pow(2, 32) * (TPowerdown::config_adr + WRITE_ADDR);
    return bitset<40>(msg);
}

bitset<40> TPWMThreshold::getWriteBitset(){
    long long int msg = 0; 
    msg += TPWMThreshold::TPWMTHRS;
    msg += pow(2, 32) * (TPWMThreshold::config_adr + WRITE_ADDR);
    return bitset<40>(msg);
}

bitset<40> TCoolThreshold::getWriteBitset(){
    long long int msg = 0; 
    msg += TCoolThreshold::TCOOLTHRS;
    msg += pow(2, 32) * (TCoolThreshold::config_adr + WRITE_ADDR);
    return bitset<40>(msg);
}

bitset<40> THigh::getWriteBitset(){
    long long int msg = 0; 
    msg += THigh::THIGH;
    msg += pow(2, 32) * (THigh::config_adr + WRITE_ADDR);
    return bitset<40>(msg);
}

/*
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
  
  */