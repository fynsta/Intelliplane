#include "quaternion.h"
namespace n
{

  /*struct vector {
  float i, j, k;
};*/

  void multiply(Quaternion &a, Quaternion &b, Quaternion &result)
  {
    result.r = a.r * b.r - a.i * b.i - a.j * b.j - a.k * b.k;
    result.i = a.r * b.i + a.i * b.r + a.j * b.k - a.k * b.j;
    result.j = a.r * b.j - a.i * b.k + a.j * b.r + a.k * b.i;
    result.k = a.r * b.k + a.i * b.j - a.j * b.i + a.k * b.r;
  }
  float length(Quaternion &a)
  {
    return sqrt(a.r * a.r + a.i * a.i + a.j * a.j + a.k * a.k);
  }
  void unify(Quaternion &a)
  {
    float len = sqrt(a.r * a.r + a.i * a.i + a.j * a.j + a.k * a.k);
    if (!isnormal(len))
    {
      a.i = a.j = a.k = 0;
      a.r = 1;
      return;
    }
    a.r /= len;
    a.i /= len;
    a.j /= len;
    a.k /= len;
  }
  Quaternion invers(Quaternion a)
  {
    a.i *= -1;
    a.j *= -1;
    a.k *= -1;
    return a;
  }
  void multiply(Quaternion &q, float f)
  {
    q.i *= f;
    q.j *= f;
    q.k *= f;
    q.r *= f;
  }
  float vectorLength(Quaternion &q)
  {
    return sqrt(q.i * q.i + q.j * q.j + q.k * q.k);
  }
  void makeTurnQuaternion(Quaternion &axis, float angle)
  {
    angle /= 2;
    axis.r = cos(angle);
    float s = sin(angle);
    axis.i *= s;
    axis.j *= s;
    axis.k *= s;
  }
  Quaternion turnVector(Quaternion toTurn, Quaternion &rotation)
  {
    Quaternion result = {0, 0, 0, 0};
    multiply(rotation, toTurn, result);
    // toTurn=result;
    Quaternion inv = invers(rotation);
    multiply(result, inv, toTurn);
    return toTurn;
  }
  void rotate(Quaternion &base, Quaternion rot)
  {
    float angle = vectorLength(rot);
    if (!isnormal(angle) || angle < 1e-8)
      return;
    rot.r = cos(angle / 2);
    float s = sin(angle / 2) / angle;
    rot.i *= s;
    rot.j *= s;
    rot.k *= s;
    /*Quaternion axis = turnVector({0, 1, 0, 0}, base);
  axis.r = cos(angle);
  float s = sin(angle);
  axis.i *= s;
  axis.j *= s;
  axis.k *= s;*/
    Quaternion res = {0, 0, 0, 0};
    multiply(rot, base, res);
    base = res;
  }
  void rotateX(Quaternion &base, float angle)
  {
    angle /= 2;
    Quaternion axis = turnVector({0, 1, 0, 0}, base);
    axis.r = cos(angle);
    float s = sin(angle);
    axis.i *= s;
    axis.j *= s;
    axis.k *= s;
    Quaternion res = {0, 0, 0, 0};
    multiply(axis, base, res);
    base = res;
  }

  void rotateY(Quaternion &base, float angle)
  {
    angle /= 2;
    Quaternion axis = turnVector({0, 0, 1, 0}, base);
    axis.r = cos(angle);
    float s = sin(angle);
    axis.i *= s;
    axis.j *= s;
    axis.k *= s;
    Quaternion res = {0, 0, 0, 0};
    multiply(axis, base, res);
    base = res;
  }
  void rotateZ(Quaternion &base, float angle)
  {
    angle /= 2;
    Quaternion axis = turnVector({0, 0, 0, 1}, base);
    axis.r = cos(angle);
    float s = sin(angle);
    axis.i *= s;
    axis.j *= s;
    axis.k *= s;
    Quaternion res = {0, 0, 0, 0};
    multiply(axis, base, res);
    base = res;
  }
  Quaternion toQuaternion(float pitch, float roll,
                          float yaw) // yaw (Z), pitch (Y), roll (X)
  {
    // Abbreviations for the various angular functions
    float cy = cos(yaw * 0.5);
    float sy = sin(yaw * 0.5);
    float cp = cos(pitch * 0.5);
    float sp = sin(pitch * 0.5);
    float cr = cos(roll * 0.5);
    float sr = sin(roll * 0.5);

    Quaternion q;
    q.r = cy * cp * cr + sy * sp * sr;
    q.i = cy * cp * sr - sy * sp * cr;
    q.j = sy * cp * sr + cy * sp * cr;
    q.k = sy * cp * cr - cy * sp * sr;

    return q;
  }
  Quaternion crossProduct(Quaternion &a, Quaternion &b)
  {
    return Quaternion{0, a.j * b.k - a.k * b.j, a.k * b.i - a.i * b.k,
                      a.i * b.j - a.j * b.i};
  }
  float scalarProd(Quaternion &a, Quaternion &b)
  {
    return a.i * b.i + a.j * b.j + a.k * b.k;
  }
  void rotateAToB(Quaternion &a, Quaternion &b, Quaternion &toRotate,
                  float factor)
  {
    //unify(b);
    Quaternion axis = crossProduct(a, b);
    float len = length(axis);
    if (len == 0)
    {
      return;
    }
    multiply(axis, len);
    makeTurnQuaternion(axis, /*asin(len) * factor*/ sqrt(0.5 - 0.5 * scalarProd(a, b)) * factor);
    Quaternion res;
    multiply(axis, toRotate, res);
    toRotate = res;
  }

  void adoptAToB(Quaternion &a, Quaternion &b, float f)
  {
    float geg = 1 - f;
    a.r = geg * a.r + f * b.r;
    a.i = geg * a.i + f * b.i;
    a.j = geg * a.j + f * b.j;
    a.k = geg * a.k + f * b.k;
    unify(a);
  }
  void toPitchBank(Quaternion &q, float &pitch, float &bank, float &yaw)
  {

    // roll (x-axis rotation)
    float sinr_cosp = +2.0 * (q.r * q.i + q.j * q.k);
    float cosr_cosp = +1.0 - 2.0 * (q.i * q.i + q.j * q.j);
    bank = atan2(sinr_cosp, cosr_cosp);

    // pitch (y-axis rotation)
    float sinp = +2.0 * (q.r * q.j - q.k * q.i);
    if (fabs(sinp) >= 1)
      pitch = copysign(M_PI / 2, sinp); // use 90 degrees if out of range
    else
      pitch = asin(sinp);

    // yaw (z-axis rotation)

    float siny_cosp = +2.0 * (q.r * q.k + q.i * q.j);
    float cosy_cosp = +1.0 - 2.0 * (q.j * q.j + q.k * q.k);
    yaw = atan2(siny_cosp, cosy_cosp);

    //return angles;
  }
} // namespace n