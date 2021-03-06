from ..tools.modelToRnnCell import ModelRnn
import tensorflow as tf
layers = tf.keras.layers


def getModel(INPUT_TIME_SERIES_LENGTH=20, PARAMETER_COUNT=2, PREDICTABLE_PARAM_COUNT=1):
    """
    returns recurrent network model.   
    t0 t1 t2 t3 t4 t5
    |  |  |  |  |  |
    v  v  v  v  v  v
    L->L->L->L->L->L-----
    |  |  |  |  |  |    |
    v  v  v  v  v  v    |
    F  F  F  F  F  F    |
    |  |  |  |  |  |    |
    v  v  v  v  v  v    |
    t1 t2 t3 t4 t5 t6   |
                   |    |
                   v    |
                output <-

    L=^LSTM cell
    F=^ deep fully connected network ("output processor"). It needs to be wrapped into an RNN cell to work with the LSTM cell
    ti=^ parameters at time i
    Note that the link from the last state to the output is optional and must be enabled by setting "return_state" to true
    """
    LSTM_STATE_SIZE = 10

    def getOutputProcessor():
        procInput = layers.Input((LSTM_STATE_SIZE,))
        dense0 = layers.Dense(10, activation='relu')(procInput)
        dense1 = layers.Dense(10, activation='relu')(dense0)
        dense2 = layers.Dense(7, activation='relu')(dense1)
        output = layers.Dense(PREDICTABLE_PARAM_COUNT)(dense2)
        return tf.keras.Model(procInput, output)

    outputPorcessor = getOutputProcessor()
    outputPorcessorCell = ModelRnn(outputPorcessor)
    lstmCell = layers.LSTMCell(LSTM_STATE_SIZE)
    cell = layers.StackedRNNCells(
        [layers.LSTMCell(LSTM_STATE_SIZE), lstmCell, outputPorcessorCell])
    rnn = layers.RNN(cell, input_shape=(None,
                                        PARAMETER_COUNT,))
    model = tf.keras.Sequential([
        rnn
    ])
    return model, True
