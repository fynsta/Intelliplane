#ifndef RX_H
#define RX_H
class RX
{
public:
    /**
 * Get current value of given channel*/
    virtual float getChannel(int channel) = 0;
};
#endif