import inspect
import sys
import os
from pathlib import Path
import importlib
from os import name
from sys import path_importer_cache
from tensorflow import keras
from tensorflow.python.keras.backend import random_normal
from tf_agents.environments import tf_environment
from tf_agents.environments import py_environment
import random
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
y_ref = tf.exp(tf.linspace(start=0., stop=10., num=200))

tfp.math.interp_regular_1d_grid(
    x=[6.0, 0.5, 3.3], x_ref_min=0., x_ref_max=10., y_ref=y_ref)
STEP = 0.1
REDSIZE = 5


# def getModel():
#     elvIn = tf.keras.layers.Input(shape=(SIZE,))
#     ptchIn = tf.keras.layers.Input(shape=(SIZE,))
#     # convElv=tf.keras.layers.Conv1D(SIZE-1,5)(elvIn)
#     # convPtch=tf.keras.layers.Convolution1D(SIZE,3)(ptchIn)
#     elvLayer = tf.keras.layers.Dense(REDSIZE)(elvIn)
#     pitchLayer = tf.keras.layers.Dense(REDSIZE)(ptchIn)
#     joined = tf.keras.layers.Concatenate()([pitchLayer, elvLayer])
#     dense0 = tf.keras.layers.Dense(10, 'tanh')(joined)
#     dense1 = tf.keras.layers.Dense(5, 'tanh')(dense0)
#     outLayer = tf.keras.layers.Dense(units=1)(dense1)
#     model = tf.keras.Model(inputs=[elvIn, ptchIn], outputs=outLayer)
#     return model

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
helperDir = os.path.join(parent_dir, 'simulator', 'helper')
sys.path.insert(0, helperDir)
from tools import constants
SIZE = constants.INPUT_TIME_SERIES_LENGTH

usedModel = importlib.import_module("models."+constants.MODEL)
simulator = usedModel.getModel(SIZE)
simulator.load_weights(os.path.join(
    parent_dir, 'simulator', 'checkpoint', constants.MODEL, 'sim'))

simulator.trainable = False
simulator.summary()


def getAutopilot():
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    ptchIn = tf.keras.layers.Input(shape=(SIZE,))
    elvLayer = tf.keras.layers.Dense(REDSIZE,'sigmoid')(elvIn)
    pitchLayer = tf.keras.layers.Dense(REDSIZE, 'sigmoid')(ptchIn)
    joined = tf.keras.layers.Concatenate()([pitchLayer, elvLayer])
    dense0 = tf.keras.layers.Dense(10, 'sigmoid')(joined)
    dense1 = tf.keras.layers.Dense(5, 'sigmoid')(dense0)
    outLayer = tf.keras.layers.Dense(units=1, activation='sigmoid')(dense1)
    model = tf.keras.Model(inputs=[elvIn, ptchIn], outputs=outLayer)
    return model

def getSimpleAP():
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    ptchIn = tf.keras.layers.Input(shape=(SIZE,))
    concat=tf.keras.layers.Concatenate()([elvIn,ptchIn])
    output=tf.keras.layers.Dense(1, 'sigmoid')(concat)
    return tf.keras.Model(inputs=[elvIn, ptchIn], outputs=output)

def getHardcodedAP():
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    ptchIn = tf.keras.layers.Input(shape=(SIZE,))
    spam,output=tf.split(ptchIn,[19,1],1)
    output=0.7-output
    return tf.keras.Model(inputs=[elvIn, ptchIn], outputs=output)


ap = getHardcodedAP()
ap.summary()

def loss(y_true, y_pred):
    return tf.reduce_mean(tf.reduce_mean(tf.square(y_pred)))


def getOneStepLayer():
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    ptchIn = tf.keras.layers.Input(shape=(SIZE,))
    signal = ap([elvIn, ptchIn])
    ptch = simulator([elvIn, ptchIn])
    rst, newPtchSer = tf.split(ptchIn, [1, SIZE-1], 1)
    newPtchSer = tf.concat([newPtchSer, ptch], 1)
    rst, newElvSer = tf.split(ptchIn, [1, SIZE-1], 1)
    newElvSer = tf.concat([newElvSer, signal], 1)
    return tf.keras.Model(inputs=[elvIn, ptchIn], outputs=[newElvSer, newPtchSer, signal, ptch])


osl = getOneStepLayer()
osl.summary()
elvIn = tf.keras.layers.Input(shape=(SIZE,))
ptchIn = tf.keras.layers.Input(shape=(SIZE,))
ptchOutputs = []
e, p = elvIn, ptchIn
for i in range(15):
    e, p, eNew, pNew = osl([e, p])
    ptchOutputs.append(pNew)
#res, out = tf.split(p, [SIZE-1, 1], 1)
ptchOutputs = tf.keras.layers.concatenate(ptchOutputs)
model = tf.keras.Model(inputs=[elvIn, ptchIn], outputs=ptchOutputs)
model.summary()
tf.keras.utils.plot_model(model, 'autopilot.png')

model.compile(
    optimizer=tf.optimizers.Adam(0.001),
    loss=loss
)


def predAP(elv, pitch):
    elv = np.array([elv])
    pitch = np.array([pitch])
    res = ap.predict([elv, pitch])
    return np.asscalar(res)


def predPch(elv, pitch):
    elv = np.array([elv])
    pitch = np.array([pitch])
    res = simulator.predict([elv, pitch])
    return np.asscalar(res)


pitchSer = [0 for i in range(SIZE)]
elvSer = [0.5 for i in range(SIZE)]
for i in range(2):
    next = predPch(elvSer, pitchSer)
    nextInput = predAP(elvSer, pitchSer)
    # nextInput=0.5-next
    pitchSer.pop(0)
    elvSer.pop(0)
    pitchSer.append(next)
    print('pitch:', next, 'elv: ', nextInput)
    elvSer.append(nextInput)

# startingPoints = []
# startingInputs = []
# spam = []
# for i in range(1000):
#     grad = random.uniform(-0.001, 0.001)
#     start = random.uniform(-0.3, 0.3)
#     startingPoints.append([start+j*grad for j in range(SIZE)])
#     startingInputs.append([grad+0.5 for j in range(SIZE)])
#     spam.append(0)

base_path = Path(__file__).parent.parent
file_path = (base_path / "../dataCollection/logs/flight0.txt").resolve()
from tools import readLog, getSamples
dataSet = readLog.FlightDataSet(file_path)

startingInputs, startingPoints, spam = getSamples.load(STEP, SIZE, dataSet)
startingPoints = np.array(startingPoints)
startingInputs = np.array(startingInputs)
spam = np.array(spam)
model.fit(
    x=[startingInputs, startingPoints],
    y=spam,
    batch_size=100,
    epochs=15
)

output = model([startingInputs, startingPoints])
l = loss(0, output)

pitchSer = [0 for i in range(SIZE)]
elvSer = [0.5 for i in range(SIZE)]

while True:
    #print(model.predict([np.array([elvSer]), np.array([pitchSer])]).numpy())
    next = predPch(elvSer, pitchSer)
    nextInput = predAP(elvSer, pitchSer)
    #nextInput=0.7-next
    pitchSer.pop(0)
    elvSer.pop(0)
    pitchSer.append(next)
    print('pitch:', next, 'elv: ', nextInput)
    elvSer.append(nextInput)
