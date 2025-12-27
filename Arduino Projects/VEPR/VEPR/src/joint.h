#ifndef JOINT_H
#define JOINT_H

#include <AccelStepper.h>
#include <TMCStepper.h>

using namespace TMC2130_n;

struct MotorJoint{
    MotorJoint(uint8_t stepPin, uint8_t dirPin, uint8_t csPin, uint8_t enablePin, float rSense);
    int en_pin;

    int steps_pr = 200;

    // Main Variables
    int mot_speed;
    int mot_accel;
    float mot_reduction;

    // Homing Variables
    int mot_home_speed;
    bool mot_home_inv;
    int mot_home_accel;
    int mot_shome_offset;
    float mot_home_mult;
    float mot_home_offset;

    int mot_mcrs;
    int mot_irun;
    int mot_ihold;

    //Positional Arguments
    float current_deg = 0;
    float move_to_deg = 0;
    int move_to = 0;

    //Homing Arguments
    bool home_mot = false;
    bool second_home = false;
    bool home_slow = false;

    AccelStepper stepper;
    TMC5160Stepper driver;
    bool AreVariablesSet();
    void InitTMC();
    void EnableMotor(int enable);
    bool IsFinished();
    void SetTravel(float angle);
    float GetCurrentPosition();
};

#endif
