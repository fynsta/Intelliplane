#ifndef FloatVector_H
#define FloatVector_H
#include "Arduino.h"
struct FloatVector{
    float x=0;
    float y=0;
    float z=0;
};
void reset(FloatVector &v);
String toString(FloatVector &v);
#endif