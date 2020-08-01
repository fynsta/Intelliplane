#ifndef SERVOCONTROL_H
#define SERVOCONTROL_H
#include "RX.h"
#include <Arduino.h>
#include <Servo.h>
enum channelPins
{
    THR = PB1,
    AIL = PB0,
    ELV = PA7,
    RUD = PA6,
    FLP = PA1,
    GEAR = PA0
};
Servo servos[6];
double lastValues[6];
void initializeServos()
{
    servos[0].attach(THR);
    servos[1].attach(AIL);
    servos[2].attach(ELV);
    servos[3].attach(RUD);
    servos[4].attach(FLP);
    servos[5].attach(GEAR);
    for (int i = 1; i < 6; i++)
    {
        lastValues[i] = 0.5;
    }
}
void setServoStates(RX &rx)
{

    for (int i = 0; i < 6; i++)
    {
        lastValues[i] += 0.1 * (rx.getChannel(i) - lastValues[i]);
        servos[i].write(lastValues[i] * 90.0 + 45.0);
    }
    /*servos[0].write(180.0 * lastValues[0]);
    servos[1].write(180.0 * (0.5 * lastValues[3] + 0.5 * lastValues[2]));
    servos[2].write(180.0 * (0.5 + 0.5 * lastValues[3] - 0.5 * lastValues[2]));*/
}
#endif