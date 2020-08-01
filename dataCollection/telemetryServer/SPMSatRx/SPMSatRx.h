/*
Reciever library for Spektrum-comatible satellite recievers
Author: Ole Petersen
Email: 	peteole2707@gmail.com

Wireing:

Connect the power cables to 3.3V (orange) and GND (black). The grey cable must be connected to the RX channel of any serial port.

Binding procedure: 

Right after startup, a few pulses must be sent to the rx via its data cable to make it enter bind mode. Depending on the number of pulses it uses the following modes:
DSMX Bind Modes:
Pulses  Mode        Protocol    Type
7       Internal    DSMx        22ms
8       External    DSMx        22ms
9       Internal    DSMx        11ms
10      External    DSMx        11ms
DSM2 Bind Modes (not recommended):
Pulses  Mode        Protocol    Type
3       Internal    DSM2        22ms
4       External    DSM2        22ms
5       Internal    DSM2        11ms
6       External    DSM2        11ms 


Recieving data:

Every 22 or 11ms a data package is sent with a baud rate of 115200bps. It consists of 16 bytes. The first two are metadata and the last 14 contain the channel value information.
Information about one channel are coded into two bytes:
metadata	channel information
xx			xx	xx	xx	xx	xx	xx	xx
The channel values are not necessarily in the right order, so each channel data package consisting of two bytes contains the channel ID and its value. The data format depends on the binding type:

DSM2:
The two bytes contain 16 bits. Bits 0-9 encode the channel position and bits 10-15 the channel ID:

servo position	channel ID
xxxxxxxxxx		xxxxxx
Both values are binary integer numbers, meaning that there are 2^10=1024 possible servo positions and 2^6=64 possible channels.

DSMX:
The two bytes contain 16 bits. Bits 0-10 encode the channel position, bits 11-14 the channel ID and bit 16 sth called "servo phase", which you can ignore.

servo position	channel ID	Servo phase
xxxxxxxxxxx		xxxx		x
Both values are binary integer numbers, meaning that there are 2^11=2048 possible servo positions and 2^4=16 possible channels.


Note that these data formats do not necessarily correspond to the selected mode even though they should, so if you only get correct values for the throttle, just try selecting the other data format.

*/
#ifndef SMP_SAT_RX_H
#define SPM_SAT_RX_H
#include <Arduino.h>
#define NUM_OF_BIND_PULSES 9
enum ProtocolMode
{
	DSM2_22 = 3,
	DSM2_11 = 5,
	DSMX_22 = 7,
	DSMX_11 = 9
};
enum DataFormat
{
	DSM2,
	DSMX
};
class SPMSatRx
{
public:
	SPMSatRx(int pin, Stream *input, int numOfChannels, ProtocolMode protocolMode = ProtocolMode::DSMX_11, DataFormat dataFormat = DataFormat::DSMX);
	void bind();
	bool read();
	float getChannel(int channelId);
	const int numOfChannels;

private:
	ProtocolMode protocolMode;
	DataFormat dataFormat;
	class DSMXServoValue
	{
	private:
		uint16_t value;

	public:
		uint8_t getChannel();
		float getValue();
	};

	class DSM2ServoValue
	{
	private:
		uint16_t value;

	public:
		uint8_t getChannel();
		float getValue();
	};
	int pin;
	Stream *input;

	bool getTrans();
	short inData[16];
	short i;
	uint8_t inByte;

	unsigned short *chVal; //short
	unsigned short tempData;
	uint16_t temp;
	unsigned short tempId;
	unsigned short tempVal;
	unsigned long time;
	float *channelValues;
};
#endif