import tensorflow as tf


def getOleApModel(simulator: tf.keras.Model, autopilot: tf.keras.Model, predictionSteps: int, INPUT_TIME_SERIES_LENGTH: int, PARAMETER_COUNT=2, PREDICTABLE_PARAM_COUNT=1):
    simulator.trainable=False
    input = tf.keras.layers.Input((INPUT_TIME_SERIES_LENGTH,PARAMETER_COUNT,))
    for i in range(predictionSteps):
        