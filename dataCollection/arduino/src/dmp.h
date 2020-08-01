// file for motion procession for artificial horizon and conpass

#ifndef DMP_H
#define DMP_H


//#define gy89
//#define mpu6050
#define mpu9250

#include "Arduino.h"
#include "quaternion.h"
#include "floatVector.h"
#include "Wire.h"
//storage
extern n::Quaternion currentRotation;
extern float pitch ;
extern float bank ;
extern float gyroYaw ;


//gyro and accel
extern long lastRead;
#ifdef mpu6050
#include "MPU6050.h"
extern MPU6050 accelgyro;
#endif
#ifdef mpu9250
#include "MPU9250.h"
extern float magnetHeading;
extern MPU9250 mpu;
#endif
#ifdef gy89
#include "Adafruit_L3GD20_U.h"
#include "Adafruit_Sensor.h"
extern Adafruit_L3GD20_Unified gyro;// = Adafruit_L3GD20_Unified(20);
void readCompass();
#endif
extern FloatVector rot;
extern FloatVector accel;
extern FloatVector rotSpeed;
void beginDmp();
void readGyro();
void calibrateGyro();
void processRotations();
void readAccel();
void applyAccel();


#endif