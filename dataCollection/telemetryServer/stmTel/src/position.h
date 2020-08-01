#ifndef POSITION_H
#define POSITION_H

#include "Arduino.h"
#include "TinyGPS++.h"
//#include "SoftwareSerial.h"
#include "HardwareSerial.h"
extern HardwareSerial ss;
extern TinyGPSPlus gps;
void initializeGPS();
void readGPS();
void readGPSPart(int maxLength);
#endif