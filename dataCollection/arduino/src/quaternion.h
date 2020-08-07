#ifndef Quaternion2_H
#define Quaternion2_H

#include <math.h>
namespace n
{

  struct Quaternion
  {
    float r;
    float i;
    float j;
    float k;
  };
  /*struct vector {
  float i, j, k;
};*/

  void multiply(Quaternion &a, Quaternion &b, Quaternion &result);
  float length(Quaternion &a);
  void unify(Quaternion &a);
  Quaternion invers(Quaternion a);
  void multiply(Quaternion &q, float f);
  float vectorLength(Quaternion &q);
  void makeTurnQuaternion(Quaternion &axis, float angle);
  Quaternion turnVector(Quaternion toTurn, Quaternion &rotation);
  void rotate(Quaternion &base, Quaternion rot);

  void rotateX(Quaternion &base, float angle);

  void rotateY(Quaternion &base, float angle);
  void rotateZ(Quaternion &base, float angle);
  Quaternion toQuaternion(float pitch, float roll,
                          float yaw);
  Quaternion crossProduct(Quaternion &a, Quaternion &b);
  void rotateAToB(Quaternion &a, Quaternion &b, Quaternion &toRotate,
                  float factor);

  void adoptAToB(Quaternion &a, Quaternion &b, float f);
  void toPitchBank(Quaternion &q, float &pitch, float &bank, float &yaw);
} // namespace n
#endif