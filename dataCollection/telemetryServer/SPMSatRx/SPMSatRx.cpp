#include <SPMSatRx.h>
SPMSatRx::SPMSatRx(int pin, Stream *input, int numOfChannels, ProtocolMode protocolMode, DataFormat dataFormat) : numOfChannels(numOfChannels)
{
    this->pin = pin;
    this->input = input;
    this->chVal = new unsigned short[numOfChannels];
    this->channelValues = new float[numOfChannels];
    this->protocolMode = protocolMode;
    this->dataFormat = dataFormat;
}
void SPMSatRx::bind()
{

    pinMode(pin, OUTPUT);
    delay(100);
    for (char i = 0; i < this->protocolMode; i++)
    {
        // no documentation of requirements for pulse width but 200us and a
        // duty cycle of 50% was tested succesfully
        digitalWrite(this->pin, LOW);
        delayMicroseconds(100);
        digitalWrite(this->pin, HIGH);
        delayMicroseconds(100);
    }
    pinMode(pin, INPUT);
}
float SPMSatRx::getChannel(int channelId)
{
    return (float)this->chVal[channelId];
}
bool SPMSatRx::read(void)
{
    while (input->available() >= 16)
    {
        //input->read();
        time = millis();
        for (i = 0; i < 16; i++)
        {
            inByte = input->read();
            inData[i] = inByte;
        }
    }
    switch (this->dataFormat)
    {
    case DataFormat::DSMX:
        DSMXServoValue *values = reinterpret_cast<DSMXServoValue *>(inData);
        for (int i = 1; i < 8; i++)
        {
            int chan = values[i].getChannel();
            if (chan < 0 || chan >= numOfChannels)
                break;
            channelValues[chan] = values[i].getValue();
        }
        break;
    case DataFormat::DSM2:
        DSM2ServoValue *values = reinterpret_cast<DSM2ServoValue *>(inData);
        for (int i = 1; i < 8; i++)
        {
            int chan = values[i].getChannel();
            if (chan < 0 || chan >= numOfChannels)
                break;
            channelValues[chan] = values[i].getValue();
        }
        break;
    default:
        break;
    }
    return getTrans();
}
bool SPMSatRx::read(void)
{
    while (input->available() >= 16)
    {
        //input->read();
        time = millis();
        for (i = 0; i < 16; i++)
        {
            inByte = input->read();
            inData[i] = inByte;
        }
    }
    for (i = 1; i < 8; i++)
    {
        temp = inData[i * 2] * 256 + inData[i * 2 + 1];

        tempId = temp >> 10;

        tempVal = temp << 6;
        tempVal = tempVal >> 6;

        /*tempId = temp >> 11;

        tempVal = temp << 5;
        tempVal = tempVal >> 5;*/
        if (tempId < numOfChannels)
        {
            chVal[tempId] = tempVal; //tempVal - 342;
        }
        else
        {
            //error, ignore ;)
        }
    }

    /*while (input->available() > 0)
    {
        input->read();
    }*/
    return getTrans();
}

bool SPMSatRx::getTrans()
{
    if (millis() - time > 1000)
    {
        return false;
    }
    else
    {
        return true;
    }
}
uint8_t SPMSatRx::DSMXServoValue::getChannel()
{
    return this->value >> 11;
}
uint8_t SPMSatRx::DSM2ServoValue::getChannel()
{
    return this->value >> 10;
}
float SPMSatRx::DSMXServoValue::getValue()
{
    uint16_t tmp = this->value << 5;
    tmp = tmp >> 5;
    return ((float)tmp) / 2048.0;
}

float SPMSatRx::DSM2ServoValue::getValue()
{
    uint16_t tmp = this->value << 6;
    tmp = tmp >> 6;
    return ((float)tmp) / 1024.0;
}