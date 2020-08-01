#include "floatVector.h"
void reset(FloatVector &v){
    v.x=0;
    v.y=0;
    v.z=0;
}
String toString(FloatVector &v){
    return "("+(String)v.x+"|"+(String)v.y+"|"+(String)v.z+")";
}