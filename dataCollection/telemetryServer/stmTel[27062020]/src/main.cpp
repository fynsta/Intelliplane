#define gyroSensor
#define bmpSensor
#define HC12Module
//#define SerialDebugging
//#define NEO6M

#ifdef HC12Module
#include "sendData.h"
#endif
#include "dmp.h"
#ifdef bmpSensor
#include "height.h"
#endif
#include <Arduino.h>

#ifdef NEO6M
#include "position.h"
#endif
//#include "compass.h"
#define leftLED PA8
#define rightLED PA9
float heading = 0;
#ifndef bmpSensor
float speed = 0;
float height = 0;
#endif
int counter = 0;
String startedMessage = "";
void setup()
{
#ifdef SerialDebugging
	Serial.begin(9600);
#endif
#ifdef bmpSensor
	beginHeight();
	delay(20);
	calibrateHeight();
// beginCompass();
#endif
#ifdef HC12Module
	HC12.begin(9600);
#endif
#ifdef NEO6M
	initializeGPS();
#endif
	beginDmp();
	calibrateGyro();
	pinMode(PC13, OUTPUT);
}

void loop()
{
#ifdef bmpSensor
	readHeight();
#endif
	// readCompass();
	readGyro();
	readAccel();
#ifdef NEO6M
	readGPSPart(10);
#endif
	processRotations();
	n::toPitchBank(currentRotation, pitch, bank, gyroYaw);
	applyAccel();
#ifdef HC12Module
	//Serial.println("available: " + HC12.available());
	while (HC12.available())
	{
		char read = HC12.read();
		switch (read)
		{
		case '{':
			startedMessage = "";
			break;
		case '}':
// execute command
#ifdef SerialDebugging
			Serial.println("message: " + startedMessage);
#endif
			if (startedMessage.startsWith("setLED:"))
			{
#define setLEDLength 7
				int power = startedMessage.substring(setLEDLength).toInt();
				sendMessage("set power " + String(power));
				digitalWrite(PC13, power < 100 ? HIGH : LOW);
				analogWrite(rightLED, power);
				analogWrite(leftLED, power);
			}
			break;
		default:
			startedMessage += read;
			break;
		}
	}
	if (counter % 20 == 0)
	{
		writeStart();
		write((uint8_t)2); // head 2
		write(pitch);
		write(bank);
		write(gyroYaw);
		write(height);
		write(speed);
		writeEnd();
		readGyro();
#ifdef NEO6m
		// write gps data
		if (counter % 100 == 0)
		{
			writeStart();
			write((uint8_t)3); // head 3
			write(gps.time.value());
			write(gps.location.lat());
			write(gps.location.lng());
			writeEnd();
		}
#endif
	}
#endif
#ifdef SerialDebugging
	Serial.println("|" + (String)(pitch * 57) + "|" + (String)(bank * 57) + "|" +
				   (String)(gyroYaw * 57) + "|");
	// Serial.println("a " + toString(accel) + " rot " + toString(rotSpeed));
// Serial.println((String)atan2(accel.x,accel.z)+"|"+(String)atan2(accel.y,accel.z));
#endif
	counter++;
}