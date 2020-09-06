import tensorflow as tf
import tensorflow.keras.layers as layers
from pathlib import Path
import numpy as np

from ..tools import readLog
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
dataSet = readLog.FlightDataSet(file_path)

HISTORY_LENGTH=20
def getSingleTimeStepProcessor():
    input=layers.Input(shape=(11,))
    y=layers.Dense(units=10,activation='tanh')(input)
    y=layers.Dense(units=7,activation='tanh')(y)
    y=layers.Dense(units=3,activation='tanh')(y)
    y=layers.Dense(units=1)(y)
    return tf.keras.Model(input,y)

stsp=getSingleTimeStepProcessor()
def getRNN_Model():
    elvHist=layers.Input(shape=(HISTORY_LENGTH,),name='elvHistory')
    pchHist=layers.Input(shape=(HISTORY_LENGTH,),name='pchHistory')
    stacked=tf.stack([elvHist,pchHist],axis=-1)
    lstm=layers.LSTM(11, return_sequences=True)(stacked)
    outputs=[]
    for i in range(HISTORY_LENGTH):
        tsInput=lstm[:,i]
        nextOut=stsp(tsInput)
        outputs.append(nextOut)
    unifiedOut=tf.concat(values=outputs,axis=1)
    return tf.keras.Model([elvHist,pchHist],unifiedOut)
model=getRNN_Model()
model.summary()



STEP = 0.1
def getSamples():
    startTime = 0
    pitchSer = []
    elvSer = []
    labels = []
    while startTime+STEP*HISTORY_LENGTH < dataSet.length:
        elvFrame = []
        pitchFrame = []
        for i in range(0, HISTORY_LENGTH):
            frame = dataSet[startTime+i*STEP]
            elvFrame.append(frame.rx.elv)
            pitchFrame.append(frame.basic.p)
        pitchSer.append(pitchFrame)
        elvSer.append(elvFrame)
        newLabel=pitchFrame.copy()
        newLabel.pop(0)
        newLabel.append(dataSet[startTime+STEP*HISTORY_LENGTH].basic.p)
        labels.append(newLabel)
        startTime += 1
    return elvSer, pitchSer, labels

xdata, ydata, labels = getSamples()
# xdata=tf.data.Dataset.from_tensors(xdata)
# ydata=tf.data.Dataset.from_tensors(ydata)
xdata = np.array(xdata)
ydata = np.array(ydata)
labels = np.array(labels)
model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss=tf.losses.mse
)
model.fit(
    x=[xdata, ydata],
    y=labels,
    batch_size=50,
    epochs=150
)


def pred(elv, pitch):
    elv = np.array([elv])
    pitch = np.array([pitch])
    res = model.predict([elv, pitch])
    return np.asscalar(res[0,-1])


pitchSer = [0 for i in range(HISTORY_LENGTH)]
elvSer = [0.5 for i in range(HISTORY_LENGTH)]
while True:
    next = pred(elvSer, pitchSer)
    print(next)
    pitchSer.pop(0)
    elvSer.pop(0)
    pitchSer.append(next)
    elvSer.append(float(input()))