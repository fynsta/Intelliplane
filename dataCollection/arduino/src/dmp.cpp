#define gyroFactor 0.00013316211  // pi/180*250/32767
#define accelFactor 0.00059877315 // 9.81*2/32767
//#define SerialDebugging
#include "dmp.h"
#ifdef MPU6050_SENSOR
void MPU6050DMP::begin()
{
	Wire.begin();
	accelgyro.initialize();
	lastRead = micros();
	//readAccel();
	//down={0,accel.x,accel.y,accel.z};
}
void MPU6050DMP::readGyro()
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
void MPU6050DMP::calibrateGyro()
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
void MPU6050DMP::readAccel()
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
#ifdef L3GD20
void L3GD20DMP::begin()
{
	gyro.enableAutoRange(true);
	gyro.begin();
	lastRead = millis();
}
void L3GD20DMP::readGyro()
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

void L3GD20DMP::readAccel()
{
	gyro.getEvent(&event);
	accel.x = event.acceleration.x;
	accel.y = event.acceleration.y;
	accel.z = event.acceleration.z;
	// Serial.println("a" + toString(accel));
}
#endif
void DMP::processRotations()
{
	n::Quaternion axis = {0, rot.x, rot.y, rot.z};
	axis = n::turnVector(axis, currentRotation);
	float angle = n::vectorLength(axis);
	n::unify(axis);
	n::makeTurnQuaternion(axis, angle);
	n::Quaternion tmp;
	n::multiply(axis, currentRotation, tmp);
	currentRotation = tmp;
	n::unify(tmp);
	rot.x = 0;
	rot.y = 0;
	rot.z = 0;
}
void DMP::processAcceleration()
{
	n::Quaternion acceleration{0, accel.x, accel.y, accel.z};
	n::unify(acceleration);
	if (acceleration.r == 1)
		return; // acceleration was zero
	n::Quaternion currentLot = {0, 0, 0, -1};
	n::Quaternion measuredLot = n::turnVector(acceleration, currentRotation);
	n::rotateAToB(measuredLot, currentLot, currentRotation, 0.003);
	n::unify(currentRotation);
}
void DMP::processHeadingData(float headingRad,float factor){
	n::Quaternion measuredHead=n::turnVector({0,1,0,0},currentRotation);
	n::Quaternion targetHead={0,cos(headingRad),sin(headingRad),0};
	n::rotateAToB(measuredHead,targetHead,currentRotation,factor);
}
#ifdef MPU9250_SENSOR
void MPU9250DMP::readGyro()
{
	long newTime = micros();
	float dt = ((float)(newTime - lastRead)) / 1000000.0;
	lastRead = newTime;
	mpu.readSensor();
	rot.x += dt * mpu.getGyroX_rads();
	rot.y += dt * mpu.getGyroY_rads();
	rot.z += dt * mpu.getGyroZ_rads();
}

void MPU9250DMP::readAccel()
{
	accel.x = mpu.getAccelX_mss();
	accel.y = mpu.getAccelY_mss();
	accel.z = mpu.getAccelZ_mss();
}
void MPU9250DMP::begin()
{
	mpu.begin();
	lastRead = micros();
}
#endif
void DMP::calibrateOrientation(CalibrationState s)
{
	switch (s)
	{
	case CalibrationState::flatten:
	{
		translation = n::invers(currentRotation);
	}
	break;

	case CalibrationState::turn:
	{
		n::Quaternion toDraw = currentRotation;
		n::multiply(translation, currentRotation, toDraw);
	}
	break;
	default:
		break;
	}
}
void DMP::updateReadables()
{
	n::Quaternion toDraw;
	n::multiply(currentRotation, translation, toDraw);
	n::toPitchBank(toDraw, pitch, bank, yaw);
}