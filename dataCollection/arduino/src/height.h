#include <Arduino.h>
//#define BMP085_Sensor
//#define BME280_Sensor
//#define BME280_Sensor_Adafruit
#define BMP280_SENSOR
void readHeight();
void beginHeight();
float height = 0;
float speed = 0;
float pressureDifferenceOffset = 0;
float referencePressure = 0;
#define rho 1.29
#ifdef BMP085_Sensor
#include "Adafruit_BMP085.h"
#include "Adafruit_Sensor.h"
void beginHeight()
{
}
Adafruit_BMP085 bmp;
void readHeight()
{
    height = bmp.readAltitude();
}
#endif
#ifdef BME280_Sensor

#include <Wire.h>
#include <math.h>
#include "SparkFunBME280.h"
BME280 totalPressure;
BME280 staticPressure;
TwoWire Wire2(2);
void readHeight()
{
    height = staticPressure.readFloatAltitudeMeters();
#ifdef SerialDebugging
    //Serial.println("height: "+String(height));
#endif
    float p_stau = totalPressure.readFloatPressure() - staticPressure.readFloatPressure() - pressureDifferenceOffset;
    speed = sqrt(abs(p_stau * 2 / rho)) * (p_stau > 0 ? 1 : -1);
}
void beginHeight()
{
    Wire2.begin();
    totalPressure.setI2CAddress(0x77);
    totalPressure.beginI2C(Wire2);
    totalPressure.setPressureOverSample(2);
    staticPressure.setI2CAddress(0x76);
    staticPressure.beginI2C(Wire2);
    staticPressure.setPressureOverSample(2);
}
void calibrateHeight()
{
    float currentPressure = staticPressure.readFloatPressure();
    staticPressure.setReferencePressure(currentPressure);
    pressureDifferenceOffset = totalPressure.readFloatPressure() - staticPressure.readFloatPressure();
}
#endif
#ifdef BME280_Sensor_Adafruit
#include <Adafruit_BME280.h>
Adafruit_BME280 totalPressure;
Adafruit_BME280 staticPressure;
TwoWire Wire2(2);

void beginHeight()
{
    Wire2.begin();
    totalPressure.begin(0x77, &Wire2);
    staticPressure.begin(0x76, &Wire2);
}
void calibrateHeight()
{
    referencePressure = staticPressure.readPressure();
    pressureDifferenceOffset = totalPressure.readPressure() - staticPressure.readPressure();
}
void readHeight()
{
    height = staticPressure.readAltitude();
#ifdef SerialDebugging
    //Serial.println("height: "+String(height));
#endif
    float p_stau = totalPressure.readPressure() - staticPressure.readPressure() - pressureDifferenceOffset;
    speed = sqrt(abs(p_stau * 2 / rho)) * (p_stau > 0 ? 1 : -1);
}
#endif

#ifdef BMP280_SENSOR
#include "Adafruit_BMP280.h"
Adafruit_BMP280 bmp(&Wire); // use I2C interface
bool working = false;
float calibrationPressure = 1013 * 100;
void calibrateHeight()
{
    calibrationPressure = bmp.readPressure();
}
void beginHeight()
{
    working = bmp.begin(0x76);
    calibrateHeight();
}
void readHeight()
{
    height = bmp.readAltitude();
}
#endif