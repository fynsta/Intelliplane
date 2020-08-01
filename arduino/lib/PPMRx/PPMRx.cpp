#include "PPMRx.h"
PPMRx *instance;
void runInterrupt()
{
    /*if (PPMRx::getInstance() != NULL)
        PPMRx::getInstance()->read_me();*/
    instance->handleInterrupt();
}
void PPMRx::handleInterrupt()
{
    unsigned long previousMicros = microsAtLastPulse;
    microsAtLastPulse = micros();
    unsigned long time = microsAtLastPulse - previousMicros;

    if (time > blankTime)
    {
        /* If the time between pulses was long enough to be considered an end
         * of a signal frame, prepare to read channel values from the next pulses */
        pulseCounter = 0;
    }
    else
    {
        // Store times between pulses as channel values
        if (pulseCounter < numOfChannels)
        {
            if (abs(rawValues[pulseCounter] - time) < 10)
            {
                if (time >= minChannelValue - channelValueMaxError && time <= maxChannelValue + channelValueMaxError)
                {
                    validValues[pulseCounter] = constrain(time, minChannelValue, maxChannelValue);
                }
            }
            rawValues[pulseCounter] = time;
        }
        ++pulseCounter;
    }
}
PPMRx::PPMRx(int pin, int numOfChannels) : pin(pin), numOfChannels(numOfChannels)
{
    instance = this;

    rawValues = new unsigned long[numOfChannels];
    validValues = new unsigned long[numOfChannels];
    for (int i = 0; i < numOfChannels; ++i)
    {
        rawValues[i] = 0;
        validValues[i] = 0;
    }
}
PPMRx::~PPMRx()
{
    delete[] rawValues;
    delete[] validValues;
}
bool PPMRx::begin()
{
    pinMode(pin, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(pin), runInterrupt, FALLING);
    // enabling interrupt at pin 2
    return true;
}
void PPMRx::stop()
{
    detachInterrupt(digitalPinToInterrupt(pin));
    pinMode(pin, OUTPUT);
}

float PPMRx::getChannel(int channel)
{
    if (channel < 0 || channel >= numOfChannels)
        return NAN;
    noInterrupts();
    float value = (float)(validValues[channel] - minChannelValue) / (float)(maxChannelValue - minChannelValue);
    interrupts();
    return value;
}
PPMRx *PPMRx::getInstance()
{
    return instance;
}