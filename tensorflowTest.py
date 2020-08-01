import tensorflow as tf


def f(x: tf.Variable) -> tf.Variable:
    return x*x-2*x+1


with tf.GradientTape(persistent=False) as tape:
    trainable = tf.Variable(3.)
    y = trainable*trainable
    x1 = f(trainable)
print(tape.gradient(x1, trainable))