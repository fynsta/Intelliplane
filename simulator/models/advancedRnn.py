from tensorflow.python.keras.layers.recurrent import LSTMCell
import tensorflow as tf
from ..tools.modelToRnnCell import ModelRnn
layers = tf.keras.layers


def getModel(INPUT_TIME_SERIES_LENGTH: int, PARAMETER_COUNT: int, PREDICTABLE_PARAM_COUNT: int = 1):
    input = layers.Input((INPUT_TIME_SERIES_LENGTH, PARAMETER_COUNT,))
    inputModel = tf.keras.Sequential([
        layers.Dense(PARAMETER_COUNT, 'relu'),
        layers.Dense(PARAMETER_COUNT, 'relu')
    ])
    inputCell = ModelRnn(inputModel)
    lstmCell = LSTMCell(20)
    unifiedCell = layers.StackedRNNCells([inputCell, lstmCell])
    rnnLayer = layers.RNN(unifiedCell)(input)
    dense1 = layers.Dense(15, 'relu')(rnnLayer)
    dense2 = layers.Dense(10, 'relu')(dense1)
    output = layers.Dense(PARAMETER_COUNT, 'relu')(dense2)
    return tf.keras.Model(input, output)