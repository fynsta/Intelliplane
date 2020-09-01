import tensorflow as tf




class MyCell(tf.keras.layers.AbstractRNNCell):
    def __init__(self,units:int, **args):
        super(MyCell, self).__init__(**args)
        self.units=units
        self.lstm=tf.keras.layers.LSTMCell(units)

    @property
    def state_size(self):
        return self.lstm.state_size

    def build(self,input_shape):
        self.dense0=tf.keras.layers.Dense(10,tf.keras.activations.tanh,input_shape=input_shape)
        self.dense1=tf.keras.layers.Dense(15,tf.keras.activations.tanh)
        self.built=True
    def call(self, inputs, states):
        y=self.dense0(inputs)
        y,nextStates=self.lstm(y,states)
        y=self.dense1(y)
        return y,nextStates


inputTensor=tf.keras.layers.Input((17,6,))
cell=MyCell(10)
myRnn=tf.keras.layers.RNN(cell,return_sequences=True)
output=myRnn(inputTensor)
print(output)