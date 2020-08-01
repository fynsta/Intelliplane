#define gyroSensor
//#define bmpSensor
#define HC12Module
//#define SerialDebugging
#define NEO6M
//#define SPMSAT
#define SERVO_CONTROL
#define PPMRX

#ifdef HC12Module
#include "sendData.h"
#include "Servo.h"
#endif
#include "dmp.h"
#ifdef bmpSensor
#include "height.h"
#endif
#include <Arduino.h>
#include "servoControl.h"
#include <HardwareSerial.h>

#ifdef NEO6M
#include "position.h"
#endif
//#include "compass.h"
#define leftLED PB8
#define rightLED PB9
float heading = 0;
#ifndef bmpSensor
float speed = 0;
float height = 0;
#endif
int counter = 0;
String startedMessage = "";
#ifdef SPMSAT
#include "SPMSatRx.h"
SPMSatRx rx(PA12, &Serial2, 6, DSM2_22, DSM2);
#define BIND_PIN PA4
#endif
#ifdef PPMRX
#include "PPMRx.h"
PPMRx rx(PA12, 6);
#endif
void setup()
{
#ifdef SPMSAT
	pinMode(BIND_PIN, INPUT_PULLUP);
	if (digitalRead(BIND_PIN) == LOW)
		rx.bind();
	pinMode(BIND_PIN, OUTPUT);
	Serial2.begin(125000);
#endif
#ifdef PPMRX
	rx.begin();
#endif
	Wire.begin();
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
	//calibrateGyro();
	pinMode(PC13, OUTPUT);
	//Serial.begin(9600);
	initializeServos();
}

void loop()
{
#ifdef bmpSensor
	readHeight();
#endif
// readCompass();
#ifdef SPMSAT
	rx.read();
#endif
	if (counter % 100 == -1)
	{
		String msg;
		for (int i = 0; i < rx.numOfChannels; i++)
		{
			float val = rx.getChannel(i);
			//Serial.print("<" + String(i) + ":" + String(val) + ">");
			msg += "<" + String(i) + ":" + String(val) + ">";
		}
		addMessage(msg);
	}
	//Serial.println("");
	setServoStates(rx);
	readGyro();
	readAccel();
#ifdef NEO6M
	readGPSPart(2);
#endif
	processRotations();
	n::toPitchBank(currentRotation, pitch, bank, gyroYaw);
	applyAccel();
#ifdef HC12Module
	//Serial.println("available: " + HC12.available());
	//delay(50);
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
				addMessage("set power " + String(power));
				digitalWrite(PC13, power < 100 ? HIGH : LOW);
				analogWrite(rightLED, power);
				analogWrite(leftLED, power);
			}

			startedMessage = "";
			break;
		default:
			startedMessage += read;
			break;
		}
	}
	if (counter % 30 == 0)
	{
		writeStart();
		write((uint8_t)2); // head 2
		write(pitch);
		write(bank);
		write(-gyroYaw);
		write(height);
		write(speed);
		writeEnd();

		writeStart();
		write<uint8_t>((uint8_t)5); // head 3
		write<uint8_t>(rx.numOfChannels);
		for (int i = 0; i < rx.numOfChannels; i++)
		{
			write(rx.getChannel(i));
		}
		writeEnd();
		//readGyro();
#ifdef NEO6M
		// write gps data
		if (counter % 100 == 0)
		{
			writeStart();
			write<uint8_t>((uint8_t)3); // head 3
			write(gps.time.value());
			if (gps.location.isUpdated())
			{
				write<double>(gps.location.lat());
				write<double>(gps.location.lng());
			}
			else
			{
				write<double>(NAN);
				write<double>(NAN);
			}
			writeEnd();
		}
#endif
	}
	flushMessages();
#endif
#ifdef SerialDebugging
	//Serial.println("|" + (String)(pitch * 57) + "|" + (String)(bank * 57) + "|" +
	//			   (String)(gyroYaw * 57) + "|");
	// Serial.println("a " + toString(accel) + " rot " + toString(rotSpeed));
// Serial.println((String)atan2(accel.x,accel.z)+"|"+(String)atan2(accel.y,accel.z));
#endif
	counter++;
}