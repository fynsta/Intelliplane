from tf_agents.environments import tf_environment
from tf_agents.environments import py_environment
import tensorflow as tf

SIZE = 20
STEP = 0.1
REDSIZE = 5


def getModel():
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    ptchIn = tf.keras.layers.Input(shape=(SIZE,))
    # convElv=tf.keras.layers.Conv1D(SIZE-1,5)(elvIn)
    # convPtch=tf.keras.layers.Convolution1D(SIZE,3)(ptchIn)
    elvLayer = tf.keras.layers.Dense(REDSIZE)(elvIn)
    pitchLayer = tf.keras.layers.Dense(REDSIZE)(ptchIn)
    joined = tf.keras.layers.Concatenate()([pitchLayer, elvLayer])
    dense0 = tf.keras.layers.Dense(10, 'tanh')(joined)
    dense1 = tf.keras.layers.Dense(5, 'tanh')(dense0)
    outLayer = tf.keras.layers.Dense(units=1)(dense1)
    model = tf.keras.Model(inputs=[elvIn, ptchIn], outputs=outLayer)
    return model


simulator = getModel()
simulator.load_weights(
    '/home/olep/Dropbox/Intelliplane/Intelliplane/simulator/checkpoint/sim')

simulator.trainable=False
simulator.summary()

def getAutopilot():
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    ptchIn = tf.keras.layers.Input(shape=(SIZE,))
    elvLayer = tf.keras.layers.Dense(REDSIZE)(elvIn)
    pitchLayer = tf.keras.layers.Dense(REDSIZE)(ptchIn)
    joined = tf.keras.layers.Concatenate()([pitchLayer, elvLayer])
    dense0 = tf.keras.layers.Dense(10, 'tanh')(joined)
    dense1 = tf.keras.layers.Dense(5, 'tanh')(dense0)
    outLayer = tf.keras.layers.Dense(units=1)(dense1)
    model = tf.keras.Model(inputs=[elvIn, ptchIn], outputs=outLayer)
    return model
ap=getAutopilot()
def loss(y_true,y_pred):
    return tf.reduce_mean(tf.sqrt(y_pred))

def getOneStepLayer():
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    ptchIn = tf.keras.layers.Input(shape=(SIZE,))
    signal=ap([elvIn,ptchIn])
    ptch=simulator([elvIn,ptchIn])
    rst,newPtchSer=tf.split(ptchIn,[1,SIZE-1],1)
    newPtchSer=tf.concat([newPtchSer,ptch],1)
    rst, newElvSer=tf.split(ptchIn,[1,SIZE-1],1)
    newElvSer=tf.concat([newElvSer,signal],1)
    return tf.keras.Model(inputs=[elvIn,ptchIn],outputs=[newElvSer,newPtchSer])
osl=getOneStepLayer()
osl.summary()
elvIn = tf.keras.layers.Input(shape=(SIZE,))
ptchIn = tf.keras.layers.Input(shape=(SIZE,))
e,p=elvIn,ptchIn
for i in range(10):
    e,p=osl([e,p])
res,out=tf.split(p,[SIZE-1,1],1)
model=tf.keras.Model(inputs=[elvIn,ptchIn],outputs=out)
model.summary()
tf.keras.utils.plot_model(model,'autopilot.png')

model.compile(
    optimizer=tf.optimizers.RMSprop(),
    loss=loss
)