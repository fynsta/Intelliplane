import tensorflow as tf
from pathlib import Path
import numpy as np

from tools import readLog
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
dataSet = readLog.FlightDataSet(file_path)

SIZE = 20
STEP = 0.1
REDSIZE = 5


def genSample():
    startTime = dataSet.length/3
    while startTime < dataSet.length:
        pitchSeries = []
        elvSeries = []
        i = startTime
        while i < startTime+(SIZE-0.5)*STEP:
            frame = dataSet[i]
            pitchSeries.append(frame.basic.p)
            elvSeries.append(frame.rx.elv)
            i += STEP
        target = dataSet[startTime+SIZE*STEP].basic.p
        yield pitchSeries, elvSeries, target
        startTime += 1

tfData = tf.data.Dataset.from_generator(
    genSample, output_types=(tf.float32, tf.float32, tf.float32))

wElv = tf.Variable(tf.random.uniform([SIZE, REDSIZE], -0.1, 0.1), name="elvW")
wPitch = tf.Variable(tf.random.uniform([SIZE, REDSIZE], -0.1, 0.1), name="pW")
wTotal = tf.Variable(tf.random.uniform([REDSIZE*2, 1], -0.1, 0.1), name="tW")


def genFrame(pitchSer: tf.Tensor, elvSer: tf.Tensor):
    elvProc = elvSer @ wElv
    pitchProc = tf.matmul(pitchSer, wPitch)
    joined = tf.concat([elvProc, pitchProc], 1)
    joined = tf.nn.tanh(joined)
    out = tf.matmul(joined, wTotal)
    return out


def getSamples():
    startTime = 0
    pitchSer = []
    elvSer = []
    labels = []
    while startTime+STEP*SIZE < dataSet.length:
        elvFrame = []
        pitchFrame = []
        for i in range(0, SIZE):
            frame = dataSet[startTime+i*STEP]
            elvFrame.append(frame.rx.elv)
            pitchFrame.append(frame.basic.p)
        pitchSer.append(pitchFrame)
        elvSer.append(elvFrame)
        labels.append(dataSet[startTime+STEP*SIZE].basic.p)
        startTime += 1
    return elvSer, pitchSer, labels

from models import basicModel as model
model = model.getModel(SIZE, REDSIZE)

tf.keras.utils.plot_model(model)
model.summary()
model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss=tf.losses.mse
)