#include <SPMSatRx.h>
SPMSatRx::SPMSatRx(int pin, Stream *input, int numOfChannels, ProtocolMode protocolMode, DataFormat dataFormat) : numOfChannels(numOfChannels)
{
    this->pin = pin;
    this->input = input;
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
    return this->channelValues[channelId];
}
bool SPMSatRx::read(void)
{
    if (input->available() % 16 != 0)
    {
        while (input->available() > 0)
        {
            input->read();
        }
        return false;
    }
    while (input->available() >= 16)
    {
        //input->read();
        time = millis();
        for (short i = 0; i < 16; i++)
        {
            inByte = input->read();
            inData[i] = inByte;
        }
        switch (this->dataFormat)
        {
        case DataFormat::DSMX:
        {
            for (int i = 1; i < 8; i++)
            {
                uint16_t val = inData[i * 2] * 256 + inData[i * 2 + 1];
                int chan = DSMXServoValue::getChannel(val);
                if (chan < 0 || chan >= numOfChannels)
                    break;
                channelValues[chan] = DSMXServoValue::getValue(val);
            }
            break;
        }
        case (DataFormat::DSM2):
        {
            for (int i = 1; i < 8; i++)
            {
                uint16_t val = inData[i * 2] * 256 + inData[i * 2 + 1];
                int chan = DSM2ServoValue::getChannel(val);
                if (chan < 0 || chan >= numOfChannels)
                    break;
                channelValues[chan] = DSM2ServoValue::getValue(val);
            }
            break;
        }
        default:
            break;
        }
    }
    while (input->available() > 0)
    {
        input->read();
    }
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
uint8_t SPMSatRx::DSMXServoValue::getChannel(const uint16_t &value)
{
    return value >> 11;
}
uint8_t SPMSatRx::DSM2ServoValue::getChannel(const uint16_t &value)
{
    return value >> 10;
}
float SPMSatRx::DSMXServoValue::getValue(const uint16_t &value)
{
    uint16_t tmp = value << 5;
    tmp = tmp >> 5;
    return ((float)tmp) / 2048.0;
}

float SPMSatRx::DSM2ServoValue::getValue(const uint16_t &value)
{
    uint16_t tmp = value << 6;
    tmp = tmp >> 6;
    return ((float)tmp) / 1024.0;
}