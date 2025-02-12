#include <vector>
#include <bitset>

using namespace std;


class ChopConfig{
    public:
      int config_adr = 0x6C;
  
      bitset<40> getWriteBitset();
  
      static vector<bool> config;
};
  
class GConfig{
    public:
      int config_adr = 0x00;
      
      bitset<40> getWriteBitset();
  
      static vector<bool> config;
};
  
class PWMConfig{
    public:
      int config_adr = 0x70;
      
      bitset<40> getWriteBitset();
  
      static vector<bool> config;
};
  
class CoolConfig{
    public:
      int config_adr = 0x6D;
      
      bitset<40> getWriteBitset();
  
      static vector<bool> config;
};
  
class IHold_IRun{
    public:
      int config_adr = 0x10;

      bitset<40> getWriteBitset();

      int IHOLD = 20; //1-32
      int IRUN = 20; //1-32
      int IHOLDDELAY = 0; //1-16
};
  
class TPowerdown{
    public:
      int config_adr = 0x11;
  
      bitset<40> getWriteBitset();
  
      int TPOWERDOWN = 0; //0-255
};

class TPWMThreshold{
    public:
      int config_adr = 0x13;
  
      bitset<40> getWriteBitset();
  
      int TPWMTHRS = 20; //0-1'048'576
};
  
class TCoolThreshold{
    public:
      int config_adr = 0x14;
  
      bitset<40> getWriteBitset();
  
      int TCOOLTHRS = 0xFFFFF; //0-1'048'576
};
  
class THigh{
    public:
      int config_adr = 0x15;
  
      bitset<40> getWriteBitset();
  
      int THIGH = 0; //0-1'048'576
};
  