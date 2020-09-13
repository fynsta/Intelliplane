import tensorflow as tf


class ModelRnn(tf.keras.layers.AbstractRNNCell):
    def __init__(self, model: tf.keras.Model, **args):
        super(ModelRnn, self).__init__(**args)
        self.model = model

    @property
    def state_size(self):
        return 0

    @property
    def output_size(self):
        return self.model.output_shape
    def build(self, input_shape):
        # self.model.build(input_shape)
        self.built = True

    def call(self, inputs, states):
        y = self.model(inputs)
        return y, states
