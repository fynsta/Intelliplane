#define gyroFactor 0.00013316211  // pi/180*250/32767
#define accelFactor 0.00059877315 // 9.81*2/32767
//#define SerialDebugging
#include "dmp.h"
n::Quaternion currentRotation = {1, 0, 0, 0};
float pitch = 0;
float bank = 0;
float gyroYaw = 0;
long lastRead = 0;
FloatVector rot;
FloatVector rotSpeed;
FloatVector accel;
#ifdef mpu6050
MPU6050 accelgyro;
//n::Quaternion down;
void beginDmp()
{
	Wire.begin();
	accelgyro.initialize();
	lastRead = millis();
	//readAccel();
	//down={0,accel.x,accel.y,accel.z};
}
void readGyro()
{
	int16_t x;
	int16_t y;
	int16_t z;
	accelgyro.getRotation(&x, &y, &z);
	long newTime = millis();
	float dt = ((float)(newTime - lastRead)) / 1000.0;
	lastRead = newTime;
	rot.x += dt * gyroFactor * (float)x;
	rot.y += dt * gyroFactor * (float)y;
	rot.z += dt * gyroFactor * (float)z;
	rotSpeed.x = gyroFactor * (float)x;
	rotSpeed.y = gyroFactor * (float)y;
	rotSpeed.z = gyroFactor * (float)z;
	// Serial.println("rot" + toString(rot));
}
void calibrateGyro()
{
	accelgyro.setXGyroOffset(-13);
	accelgyro.setYGyroOffset(-18);
	accelgyro.setZGyroOffset(4);
	return;
	accelgyro.CalibrateGyro(12);
	Serial.println((String)accelgyro.getXGyroOffset() + "|" +
				   (String)accelgyro.getYGyroOffset() + "|" +
				   (String)accelgyro.getZGyroOffset());
	return;
	/*const int amount = 1000;
  int xSum = 0;
  int ySum = 0;
  int zSum = 0;
  for (int i = 0; i < amount; i++) {
    int16_t x;
    int16_t y;
    int16_t z;
    accelgyro.getRotation(&x, &y, &z);
    xSum+=x;
    ySum+=y;
    zSum+=z;
    //delay(1);
    Serial.println((String)x+"|"+(String)y+"|"+(String)z);
  }
  accelgyro.setXGyroOffset(xSum/amount);
  accelgyro.setYGyroOffset(ySum/amount);
  accelgyro.setZGyroOffset(zSum/amount);*/
}
void readAccel()
{
	int16_t x;
	int16_t y;
	int16_t z;
	accelgyro.getAcceleration(&x, &y, &z);
	accel.x = accelFactor * (float)x;
	accel.y = accelFactor * (float)y;
	accel.z = accelFactor * (float)z;
	// Serial.println("a" + toString(accel));
}
#endif
#ifdef gy89
Adafruit_L3GD20_Unified gyro(20);
sensors_event_t event;
void beginDmp()
{
	gyro.enableAutoRange(true);
	gyro.begin();
	lastRead = millis();
}
void readGyro()
{
	gyro.getEvent(&event);
	long newTime = millis();
	float dt = ((float)(newTime - lastRead)) / 1000.0;
	lastRead = newTime;
	rot.x += dt * event.gyro.x;
	rot.y += dt * event.gyro.y;
	rot.z += dt * event.gyro.z;
	rotSpeed.x = event.gyro.x;
	rotSpeed.y = event.gyro.y;
	rotSpeed.z = event.gyro.z;
}

void readAccel()
{
	gyro.getEvent(&event);
	accel.x = event.acceleration.x;
	accel.y = event.acceleration.y;
	accel.z = event.acceleration.z;
	// Serial.println("a" + toString(accel));
}
void calibrateGyro() {}
#endif
#ifdef mpu9250
MPU9250 mpu(Wire, 0x68);
float magnetHeading = 0;
void beginDmp()
{
	mpu.begin();
}
void readGyro()
{
	long newTime = millis();
	float dt = ((float)(newTime - lastRead)) / 1000.0;
	lastRead = newTime;
	mpu.readSensor();
	rot.y += dt * mpu.getGyroX_rads();
	rot.x += dt * mpu.getGyroY_rads();
	rot.z += dt * mpu.getGyroZ_rads();
	//magnetHeading=atan2(mpu.getMagY_uT(),mpu.getMagX_uT());
}
void readAccel()
{
	accel.y = mpu.getAccelX_mss();
	accel.x = mpu.getAccelY_mss();
	accel.z = -mpu.getAccelZ_mss();
}
void calibrateGyro()
{
	mpu.calibrateGyro();
}
#endif
void processRotations()
{
	readGyro();
	n::rotateX(currentRotation, rot.x);
	n::rotateY(currentRotation, rot.y);
	n::rotateZ(currentRotation, rot.z);
	// n::Quaternion r{0, rot.x, rot.y, rot.z};
	// n::rotate(currentRotation, r);
	n::unify(currentRotation);
	reset(rot);
	//n::toPitchBank(currentRotation, pitch, bank, gyroYaw);
}
void applyAccel()
{
	n::Quaternion acceleration{0, accel.x, accel.y, accel.z};
	n::unify(acceleration);
	if (acceleration.r == 1)
		return; // acceleration was zero
	n::Quaternion currentLot = {0, 0, 0, -1};
	n::Quaternion measuredLot = n::turnVector(acceleration, currentRotation);
#ifdef SerialDebugging
	Serial.print((String)measuredLot.i + "|" + (String)measuredLot.j + "|" + (String)measuredLot.k + "|||");
	Serial.print((String)acceleration.i + "|" + (String)acceleration.j + "|" + (String)acceleration.k);
#endif
	n::rotateAToB(measuredLot, currentLot, currentRotation, 0.5);
	n::unify(currentRotation);
}