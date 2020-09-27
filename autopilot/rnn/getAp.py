import tensorflow as tf
layers = tf.keras.layers



import inspect
import sys
import os
from pathlib import Path
import importlib
import tensorflow as tf

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
helperDir = os.path.join(parent_dir, 'simulator')
sys.path.insert(0, helperDir)
from helper.tools.modelToRnnCell import ModelRnn
from helper.tools.constants import PREDICTABLE_PARAM_COUNT,CONTROLLABLE_PARAM_COUNT

def getAp(CONTROLLABLE_PARAMETER_COUNT=CONTROLLABLE_PARAM_COUNT, PREDICTABLE_PARAM_COUNT=PREDICTABLE_PARAM_COUNT):
    """
    get the autopilot network.

    t0 t1 t2 t3 t4 t5
    |  |  |  |  |  |
    v  v  v  v  v  v
    L->L->L->L->L->L
    |  |  |  |  |  |
    v  v  v  v  v  v
    F  F  F  F  F  F
    |  |  |  |  |  |
    v  v  v  v  v  v
    t1 t2 t3 t4 t5 t6

    L=^LSTM cell
    F=^ deep fully connected network
    """
    LSTM_STATE_SIZE = 15

    def getOutputProcessor():
        procInput = layers.Input((LSTM_STATE_SIZE,))
        dense0 = layers.Dense(15, activation='relu')(procInput)
        dense1 = layers.Dense(10, activation='relu')(dense0)
        output = layers.Dense(CONTROLLABLE_PARAMETER_COUNT, activation='sigmoid')(dense1)
        return tf.keras.Model(procInput, output)

    outputPorcessor = getOutputProcessor()
    outputPorcessorCell = ModelRnn(outputPorcessor)
    lstmCell = layers.LSTMCell(LSTM_STATE_SIZE)
    cell = layers.StackedRNNCells([lstmCell, outputPorcessorCell])
    rnn = layers.RNN(cell, input_shape=(None,
                                        PREDICTABLE_PARAM_COUNT+CONTROLLABLE_PARAMETER_COUNT,))
    model = tf.keras.Sequential([
        rnn
    ])
    return model
ap=getAp()