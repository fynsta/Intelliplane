#include "Arduino.h"

#ifndef sendData_H
#define sendData_H
#define STM32
#ifndef STM32
#include "SoftwareSerial.h"
SoftwareSerial HC12(11, 10);
#else
#define HC12 Serial3
#endif
#define maxMessages 10

int numOfMessages = 0;
String *outbox = new String[maxMessages];
template <typename T>
void write(T *toPrint, int length)
{
	length *= sizeof(T);
	uint8_t *bin = reinterpret_cast<uint8_t *>(toPrint);
	for (int i = 0; i < length; i++)
	{
		HC12.write(bin[i]);
		if (bin[i] == 255)
		{
			HC12.write((uint8_t)2);
		}
	}
}
template <typename T>
void write(T toPrint)
{
	int length = sizeof(T);
	uint8_t *bin = reinterpret_cast<uint8_t *>(&toPrint);
	for (int i = 0; i < length; i++)
	{
		HC12.write(bin[i]);
		if (bin[i] == 255)
		{
			HC12.write((uint8_t)2);
		}
	}
}
void writeStart()
{
	HC12.write((uint8_t)255);
	HC12.write((uint8_t)0);
}
void writeEnd()
{
	HC12.write((uint8_t)255);
	HC12.write((uint8_t)1);
}
void addMessage(String message)
{
	if (numOfMessages >= maxMessages)
		return;
	outbox[numOfMessages] = message;
	numOfMessages++;
}
void sendMessage(String message)
{
	writeStart();
	write((uint8_t)4);
	write((uint8_t)message.length());
	write(message.begin(), message.length());
	writeEnd();
	HC12.flush();
}
void flushMessages()
{
	for (int i = 0; i < numOfMessages; i++)
	{
		sendMessage(outbox[i]);
	}
	numOfMessages = 0;
}
#endif