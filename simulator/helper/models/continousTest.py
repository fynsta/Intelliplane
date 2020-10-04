from os import name
import tensorflow as tf
from tensorflow.python.ops.gen_math_ops import mod
import tensorflow_probability as tfp

PARAMETER_COUNT = 9
PREDICTABLE_PARAM_COUNT = 4
FRAME_COUNT = 30

layers = tf.keras.layers


class InputSelectorCell(layers.AbstractRNNCell):
    def __init__(self, **args):
        super(InputSelectorCell, self).__init__(**args)
        self.run_eagerly = True

    @property
    def state_size(self):
        return [self.lstm.state_size, [1]]

    @property
    def output_size(self):
        return self.dense1.output_shape

    def build(self, input_shape):
        DENSE_OUT_COUNT = PARAMETER_COUNT
        self.dense0 = tf.keras.layers.Dense(
            DENSE_OUT_COUNT, tf.keras.activations.tanh, name='dense0', input_shape=(PARAMETER_COUNT,))
        self.lstm = layers.LSTMCell(50)
        self.dense1 = tf.keras.layers.Dense(
            DENSE_OUT_COUNT, tf.keras.activations.tanh, name='dense1', input_shape=(50,))
        self.built = True

    # input expected to have shape (None, FRAME_COUNT, PARAMETER_COUNT)
    def call(self, inputs, states):
        lstmState = states[0]
        position = states[1]
        parameterValues = tfp.math.batch_interp_regular_1d_grid(
            position, 0, 1, inputs, axis=1)

        y = self.dense0(parameterValues)
        z, nextStates = self.lstm(y, lstmState)
        nextPosition = z[:, 0]
        z = self.dense1(z)
        return z, (nextStates, nextPosition)

    def get_initial_state(self, inputs, batch_size, dtype):
        return [self.lstm.get_initial_state(batch_size=2,dtype='float32'), [0]]


def getModel():
    """
    early stage attempt to use a linear interpolation in network, far from working
    """
    y_ref = [[[1, 1], [2, 4], [3, 9], [4, 16]],
             [[1, 1], [2, 4], [3, 9], [4, 16]]]

    y = tfp.math.batch_interp_regular_1d_grid(
        x=[[3.3]], x_ref_min=0., x_ref_max=10., y_ref=y_ref, axis=1)
    yValue = y[:, 0]
    input = layers.Input(shape=(FRAME_COUNT, PARAMETER_COUNT,))
    cell = InputSelectorCell()
    cell.build(None)
    test = cell(input[:, 0], cell.get_initial_state(None, None, None))
    rnn = layers.RNN(cell)(input)
    outDense = layers.Dense(9, 'sigmoid')(rnn)
    output = layers.Dense(PREDICTABLE_PARAM_COUNT)(outDense)
    return tf.keras.Model(input, output)


#model = getModel()
#model.summary()
