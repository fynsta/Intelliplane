#ifndef PPMRX_H
#define PPMRX_H
#include <Arduino.h>
#include "RX.h"
// The range of a channel's possible values
#define minChannelValue 1000
#define maxChannelValue 2000

/* The maximum error (in either direction) in channel value
     * with which the channel value is still considered valid */
#define channelValueMaxError 10

/* The minimum value (time) after which the signal frame is considered to
     * be finished and we can start to expect a new signal frame. */
#define blankTime 2100

class PPMRx : public RX
{
public:
    PPMRx(int pin, int numOfChannels);
    const int pin;
    const int numOfChannels;
    bool begin();
    void stop();
    float getChannel(int channel);
    static PPMRx *getInstance();
    //void read_me();
    ~PPMRx();

    void handleInterrupt();

private:
    //static PPMRx *instance;

    volatile unsigned long *rawValues = NULL;
    volatile unsigned long *validValues = NULL;
    // A counter variable for determining which channel is being read next
    volatile byte pulseCounter = 0;
    // A time variable to remember when the last pulse was read
    volatile unsigned long microsAtLastPulse = 0;
};
#endif