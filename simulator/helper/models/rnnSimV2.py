from ..tools.modelToRnnCell import ModelRnn
import tensorflow as tf
layers = tf.keras.layers


def getModel(INPUT_TIME_SERIES_LENGTH=20, PARAMETER_COUNT=2, PREDICTABLE_PARAM_COUNT=1):
    LSTM_STATE_SIZE = 15

    def getOutputProcessor():
        procInput = layers.Input((LSTM_STATE_SIZE,))
        dense0 = layers.Dense(15, activation='relu')(procInput)
        dense1 = layers.Dense(10, activation='relu')(dense0)
        output = layers.Dense(PREDICTABLE_PARAM_COUNT)(dense1)
        return tf.keras.Model(procInput, output)

    outputPorcessor = getOutputProcessor()
    outputPorcessorCell = ModelRnn(outputPorcessor)
    lstmCell = layers.LSTMCell(LSTM_STATE_SIZE)
    cell = layers.StackedRNNCells([lstmCell, outputPorcessorCell])
    rnn=layers.RNN(cell, input_shape=(None,
                                      PARAMETER_COUNT,))
    model = tf.keras.Sequential([
        rnn
    ])
    return model, True


def getCellModel(INPUT_TIME_SERIES_LENGTH=20, PARAMETER_COUNT=2, PREDICTABLE_PARAM_COUNT=1):
    LSTM_STATE_SIZE = 15
    input = layers.Input((INPUT_TIME_SERIES_LENGTH, PARAMETER_COUNT,))
    cell = layers.LSTMCell(LSTM_STATE_SIZE)
    lstm = layers.RNN(cell, return_state=True)
    processed, state_h, state_c = lstm(input)
    state = (state_h, state_c)

    def getOutputProcessor():
        procInput = layers.Input((LSTM_STATE_SIZE,))
        dense0 = layers.Dense(15, activation='relu')(procInput)
        dense1 = layers.Dense(10, activation='relu')(dense0)
        output = layers.Dense(PREDICTABLE_PARAM_COUNT)(dense1)
        return tf.keras.Model(procInput, output)

    outputProcessor = getOutputProcessor()
    output = outputProcessor(processed)
    cellStateHInput = layers.Input((cell.state_size[0],))
    cellStateCInput = layers.Input((cell.state_size[1],))
    cellInput = layers.Input((PARAMETER_COUNT,))
    cellProcessed, newCellState = cell(
        cellInput, [cellStateHInput, cellStateCInput])
    cellNetworkOutput = outputProcessor(cellProcessed)
    return tf.keras.Model(input, [output, state]), True, tf.keras.Model([cellInput, cellStateHInput, cellStateCInput], [cellNetworkOutput, newCellState]), cell


def getCell(INPUT_TIME_SERIES_LENGTH=20, CONTROLLABLE_PARAMETER_COUNT=1, PREDICTABLE_PARAM_COUNT=1):
    LSTM_STATE_SIZE = 15

    def getOutputProcessor():
        procInput = layers.Input((LSTM_STATE_SIZE,))
        dense0 = layers.Dense(15, activation='relu')(procInput)
        dense1 = layers.Dense(10, activation='relu')(dense0)
        output = layers.Dense(PREDICTABLE_PARAM_COUNT)(dense1)
        return tf.keras.Model(procInput, output)

    outputPorcessor = getOutputProcessor()
    outputPorcessorCell = ModelRnn(outputPorcessor)
    lstmCell = layers.LSTMCell(LSTM_STATE_SIZE)
    cell = layers.StackedRNNCells([lstmCell, outputPorcessorCell])
    rnn=layers.RNN(cell, input_shape=(None,
                                      PREDICTABLE_PARAM_COUNT+CONTROLLABLE_PARAMETER_COUNT,))
    model = tf.keras.Sequential([
        rnn
    ])
    return model, rnn
