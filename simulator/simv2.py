import tensorflow as tf
import tensorflow.keras.layers as layers
from pathlib import Path
import numpy as np

import tools.readLog as tools
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
# time, sets = t.readLog(file_path)
dataSet = tools.FlightDataSet(file_path)

HISTORY_LENGTH = 20


def singChanPr():
    input = layers.Input(shape=(HISTORY_LENGTH,))
    dense1 = layers.Dense(HISTORY_LENGTH/2,'tanh')(input)
    dense2 = layers.Dense(HISTORY_LENGTH/4,'tanh')(dense1)
    return tf.keras.Model(input,dense2)


def getSimulatorModel():
    elvHist = layers.Input(shape=(HISTORY_LENGTH,), name='elvHistory')
    pchHist = layers.Input(shape=(HISTORY_LENGTH,), name='pchHistory')
    altHist = layers.Input(shape=(HISTORY_LENGTH,), name='altHistory')
    velHist = layers.Input(shape=(HISTORY_LENGTH,), name='velHistory')
    bnkHist = layers.Input(shape=(HISTORY_LENGTH,), name='bnkHistory')
    elvP, pchP, altP, velP,bnkP = singChanPr()(elvHist), singChanPr()(
        pchHist), singChanPr()(altHist), singChanPr()(velHist),singChanPr()(bnkHist)
    joined=layers.concatenate([elvP,pchP,altP,velP,bnkP])
    y=layers.Dense(15,activation='tanh')(joined)
    y=layers.Dense(10,activation='tanh')(y)
    y=layers.Dense(5,activation='tanh')(y)
    y=layers.Dense(4,activation='tanh')(y)
    return tf.keras.Model([elvHist,pchHist,altHist,velHist,bnkHist],y)
model=getSimulatorModel()
model.summary()


STEP = 0.1
def getSamples():
    startTime = 0
    pitchSer = []
    elvSer = []
    altSer=[]
    velSer=[]
    bnkSer=[]
    labels = []
    while startTime+STEP*HISTORY_LENGTH < dataSet.length:
        elvFrame = []
        pitchFrame = []
        altFrame=[]
        velFrame=[]
        bnkFrame=[]
        lastAlt=dataSet[startTime+(HISTORY_LENGTH-1)*STEP].basic.a
        for i in range(0, HISTORY_LENGTH):
            frame = dataSet[startTime+i*STEP]
            elvFrame.append(frame.rx.elv)
            pitchFrame.append(frame.basic.p)
            bnkFrame.append(frame.basic.b)
            velFrame.append(frame.basic.s)
            altFrame.append(frame.basic.a-lastAlt)

        pitchSer.append(pitchFrame)
        elvSer.append(elvFrame)
        altSer.append(altFrame)
        velSer.append(velFrame)
        bnkSer.append(bnkFrame)
        labelFrame=dataSet[startTime+STEP*HISTORY_LENGTH].basic
        labels.append([labelFrame.p,labelFrame.b,labelFrame.a-lastAlt,labelFrame.s])
        startTime += 1
    return elvSer, pitchSer,bnkSer,altSer,velSer, labels

model.compile(
    optimizer=tf.optimizers.Adam(),
    loss='mse'
)

elvSer, pitchSer,bnkSer,altSer,velSer, labels=getSamples()
elvSer, pitchSer,bnkSer,altSer,velSer, labels=np.array(elvSer), np.array(pitchSer),np.array(bnkSer),np.array(altSer),np.array(velSer), np.array(labels)
model.fit(
    [elvSer, pitchSer,bnkSer,altSer,velSer],
    labels,
    batch_size=100,
    epochs=50000
)

model.save_weights('./checkpointAdvancedSim/sim')