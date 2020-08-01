#include "position.h"
HardwareSerial ss=Serial1;
TinyGPSPlus gps;
void initializeGPS(){
    ss.begin(9600);
}
void readGPS(){
    while(ss.available()){
        gps.encode(ss.read());
    }
}
void readGPSPart(int maxLength){
    for(int i=0;i<maxLength&&ss.available();i++){
        gps.encode(ss.read());
    }
}