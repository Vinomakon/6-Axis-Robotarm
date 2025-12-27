#include "joint.h"
#include <Arduino.h>

MotorJoint::MotorJoint(uint8_t stepPin, uint8_t dirPin, uint8_t csPin, uint8_t enPin, float rSense)
    : stepper(1, stepPin, dirPin)
    , driver(csPin, rSense)
{
    en_pin = enPin;
    // set sensible defaults:
    mot_speed = 0;
    mot_accel = 0;
    mot_reduction = 1.0f;
    mot_home_speed = 0;
    mot_home_accel = 0;
    mot_home_inv = false;
    mot_home_mult = 1.0f;
    mot_mcrs = 0;
    mot_irun = 0;
    mot_ihold = 0;
}

void MotorJoint::InitTMC(){
    if (mot_mcrs == 0 || mot_irun == 0 || mot_ihold == 0) return;
    driver.begin();                                                                      // Initiate pins and registeries
    driver.en_pwm_mode(1);                                                               // Enable extremely quiet stepping
    driver.toff(4);                                                                      // off time
    driver.blank_time(24);                                                               // blank tim
    driver.pwm_autoscale(1);
    driver.microsteps(mot_mcrs); // What microstep range to use
    driver.ihold(mot_ihold);
    driver.irun(mot_irun);
    driver.TPWMTHRS(20);
}

bool MotorJoint::AreVariablesSet(){
    bool ok = true;

    // Main variables
    if (mot_speed == 0) ok = false;
    if (mot_accel == 0) ok = false;
    if (mot_reduction == 0.0f) ok = false;

    // Homing variables
    if (mot_home_speed == 0) ok = false;
    if (mot_home_accel == 0) ok = false;
    // mot_home_inv is a boolean, it always has a value
    if (mot_home_mult == 0.0f) ok = false;
    // mot_home_offset could be zero legitimately; skip strict check

    // Driver configuration
    if (mot_mcrs == 0) ok = false;
    if (mot_irun == 0) ok = false;
    if (mot_ihold == 0) ok = false;
    return ok;
}

void MotorJoint::EnableMotor(int enable){
    digitalWrite(en_pin, !enable);
}

bool MotorJoint::IsFinished(){
    return (stepper.distanceToGo() == 0);
}

void MotorJoint::SetTravel(float angle){
    stepper.setMaxSpeed(mot_speed);
    stepper.setAcceleration(mot_accel);
    move_to_deg = angle;
    move_to = int((steps_pr * mot_reduction * mot_mcrs) * (move_to_deg / 360));
    stepper.moveTo(move_to);
    current_deg = move_to_deg;
}

float MotorJoint::GetCurrentPosition(){
    return current_deg;
}