// file for motion procession for artificial horizon and conpass
#define MPU9250_SENSOR
#ifndef DMP_H
#define DMP_H

#include "Arduino.h"
#include "quaternion.h"
#include "floatVector.h"
#include "Wire.h"

class DMP
{
public:
    float pitch, bank, yaw;
    enum CalibrationState
    {
        flatten,
        turn
    };
    void processHeadingData(float headingArc, float factor = 0.1);
    void updateReadables();
    n::Quaternion translation = {0.7071, 0, 0, 0.7071};
    void calibrateOrientation(CalibrationState s);
    // read gyro data and add them to the current rotations to process. Reset last read
    virtual void readGyro() = 0;
    //read acceleration data and save them in accel
    virtual void readAccel() = 0;
    // add accumulated rotations to currentRotation
    void processRotations();
    // apply acceleration to currentRotation
    void processAcceleration();
    // most recent acceleration data
    FloatVector accel;
    // accumulated rotation data
    FloatVector rot;
    n::Quaternion currentRotation = {0.7071, 0, 0, 0.7071};
};
#ifdef MPU9250_SENSOR
#include "MPU9250.h"
class MPU9250DMP : public DMP
{
public:
    MPU9250 mpu;
    MPU9250DMP() : mpu(Wire, 0x68)
    {
    }
    void readGyro() override;
    void readAccel() override;
    // begin sensor reading
    void begin();
    void calibrateGyro();

private:
    long lastRead;
};
#endif
#ifdef MPU6050_SENSOR
#include "MPU6050.h"
class MPU6050DMP : public DMP
{
public:
    MPU6050 accelgyro;
    void readGyro() override;
    void readAccel() override;
    // begin sensor reading
    void begin();
    void calibrateGyro();

private:
    long lastRead;
    FloatVector rotSpeed;
};
#endif
#ifdef L2GD20
#include "Adafruit_L3GD20_U.h"
#include "Adafruit_Sensor.h"
class L3GD20DMP : public DMP
{
public:
    Adafruit_L3GD20_Unified gyro;
    void readGyro() override;
    void readAccel() override;
    // begin sensor reading
    void begin();
    void calibrateGyro();

private:
    sensors_event_t event;
    long lastRead;
    FloatVector rotSpeed;
};
#endif
#endif