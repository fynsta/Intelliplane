import tensorflow as tf
def a(x: float) -> float:
    return 2*x

# Demonstration: Var2 is better
var1 = tf.constant([[0.0 for x in range(0, 10)]
                            for n in range(0, 10)], dtype=tf.float32)
var2 = tf.zeros([10,10], dtype=tf.float32)
print(tf.get_static_value(tf.math.reduce_all(tf.equal(var1,var2))))