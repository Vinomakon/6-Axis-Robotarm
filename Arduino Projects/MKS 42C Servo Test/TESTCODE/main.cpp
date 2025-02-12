#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <vector>

#define SWITCH_PIN 1
#define LED_PIN 48

#define DIR_PIN 46
#define STEP_PIN 3
#define DCO_PIN 8
#define SDO_PIN 18
#define CS_PIN 17
#define SCK_PIN 16
#define SDI_PIN 15
#define EN_PIN 7

#define MAX_SPEED 40
#define MIN_SPEED 1000

#define STALL_VALUE 15
#define R_SENSE 0.11f

#define ONE_ROTATION 3200

float steps_per_sec = 700;
int steps_mils = int(1000 / steps_per_sec);

String receivedMessage = "";

float current_deg = 0;
int current_pos = 0;

void setup() {
  Serial.begin(115200);

  Serial.println("ESP32 is ready!");

  pinMode(DIR_PIN, OUTPUT);
  pinMode(SWITCH_PIN, INPUT);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);
  pinMode(CS_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);

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
  bool switch_state = digitalRead(SWITCH_PIN);
  if (switch_state == HIGH){
    digitalWrite(DIR_PIN, HIGH);  
  } else {
    digitalWrite(DIR_PIN, LOW);
  }

  while(Serial.available()){
    char incomingChar = Serial.read();

    if(incomingChar == '\n'){
      Serial.println(receivedMessage);
      moveTo(receivedMessage.toFloat());
      

      receivedMessage = "";
    } else {
      receivedMessage += incomingChar;
    }
  }
  
  delayMicroseconds(int(1000 * steps_mils / 2));
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(int(1000 * steps_mils / 2));
  digitalWrite(STEP_PIN, LOW);

  // put your main code here, to run repeatedly:
}