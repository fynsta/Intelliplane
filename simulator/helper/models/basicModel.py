import tensorflow as tf

REDSIZE = 5

def getModel(SIZE):
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    pitchIn = tf.keras.layers.Input(shape=(SIZE,))
    elvLayer = tf.keras.layers.Dense(REDSIZE)(elvIn)
    pitchLayer = tf.keras.layers.Dense(REDSIZE)(pitchIn)
    joined = tf.keras.layers.Concatenate()([pitchLayer, elvLayer])
    dense0=tf.keras.layers.Dense(10,'tanh')(joined)
    dense1=tf.keras.layers.Dense(5,'tanh')(dense0)
    outLayer = tf.keras.layers.Dense(units=1)(dense1)
    model = tf.keras.Model(inputs=[elvIn, pitchIn], outputs=outLayer)
    return model