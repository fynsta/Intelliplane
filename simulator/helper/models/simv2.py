import tensorflow as tf
import tensorflow.keras.layers as layers
from pathlib import Path
import numpy as np


HISTORY_LENGTH = 20


def singChanPr():
    input = layers.Input(shape=(HISTORY_LENGTH,))
    dense1 = layers.Dense(HISTORY_LENGTH/2, 'tanh')(input)
    dense2 = layers.Dense(HISTORY_LENGTH/4, 'tanh')(dense1)
    return tf.keras.Model(input, dense2)


def getSimulatorModel():
    thrHist = layers.Input(shape=(HISTORY_LENGTH,), name='thrHistory')
    elvHist = layers.Input(shape=(HISTORY_LENGTH,), name='elvHistory')
    ailHist = layers.Input(shape=(HISTORY_LENGTH,), name='ailHistory')
    pchHist = layers.Input(shape=(HISTORY_LENGTH,), name='pchHistory')
    altHist = layers.Input(shape=(HISTORY_LENGTH,), name='altHistory')
    velHist = layers.Input(shape=(HISTORY_LENGTH,), name='velHistory')
    bnkHist = layers.Input(shape=(HISTORY_LENGTH,), name='bnkHistory')
    thrP, elvP, ailP, pchP, altP, velP, bnkP = singChanPr()(thrHist), singChanPr()(elvHist), singChanPr()(ailHist), singChanPr()(
        pchHist), singChanPr()(altHist), singChanPr()(velHist), singChanPr()(bnkHist)
    joined = layers.concatenate([thrP, elvP, ailP, pchP, altP, velP, bnkP])
    y = layers.Dense(15, activation='tanh')(joined)
    y = layers.Dense(10, activation='tanh')(y)
    y = layers.Dense(5, activation='tanh')(y)
    y = layers.Dense(4)(y)
    return tf.keras.Model([thrHist, elvHist, ailHist, pchHist, altHist, velHist, bnkHist], y)


model = getSimulatorModel()
model.summary()

import tools.readLog as tools
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
# time, sets = t.readLog(file_path)
dataSet = tools.FlightDataSet(file_path)
STEP = 0.1

def getSamples():
    startTime = 0
    thrSer = []
    elvSer = []
    ailSer = []
    pitchSer = []
    altSer = []
    velSer = []
    bnkSer = []
    labels = []
    while startTime+STEP*HISTORY_LENGTH < dataSet.length:
        thrFrame = []
        elvFrame = []
        ailFrame = []
        pitchFrame = []
        altFrame = []
        velFrame = []
        bnkFrame = []
        lastAlt = dataSet[startTime+(HISTORY_LENGTH-1)*STEP].basic.a
        for i in range(0, HISTORY_LENGTH):
            frame = dataSet[startTime+i*STEP]
            thrFrame.append(frame.rx.thr)
            elvFrame.append(frame.rx.elv)
            ailFrame.append(frame.rx.ail)
            pitchFrame.append(frame.basic.p)
            bnkFrame.append(frame.basic.b)
            velFrame.append(frame.basic.s)
            altFrame.append(frame.basic.a-lastAlt)

        pitchSer.append(pitchFrame)
        thrSer.append(thrFrame)
        elvSer.append(elvFrame)
        ailSer.append(ailFrame)
        altSer.append(altFrame)
        velSer.append(velFrame)
        bnkSer.append(bnkFrame)
        labelFrame = dataSet[startTime+STEP*HISTORY_LENGTH].basic
        labels.append([labelFrame.p, labelFrame.b,
                        labelFrame.a-lastAlt, labelFrame.s])
        startTime += 1
    return thrSer, elvSer, ailSer, pitchSer, bnkSer, altSer, velSer, labels

model.compile(
    optimizer=tf.optimizers.Adam(),
    loss='mse'
)

thrSer, elvSer, ailSer, pitchSer, bnkSer, altSer, velSer, labels = getSamples()
thrSer, elvSer, ailSer, pitchSer, bnkSer, altSer, velSer, labels = np.array(thrSer), np.array(elvSer), np.array(ailSer), np.array(
    pitchSer), np.array(bnkSer), np.array(altSer), np.array(velSer), np.array(labels)
if False:
    model.fit(
        [thrSer, elvSer, ailSer, pitchSer, bnkSer, altSer, velSer],
        labels,
        batch_size=100,
        epochs=20000
    )

    model.save_weights('./checkpointAdvancedSim/sim')
else:
    model.load_weights('./checkpointAdvancedSim/sim')


def predict(thrSer, elvSer, ailSer, pitchSer, bnkSer, altSer, velSer):
    thrSer, elvSer, ailSer, pitchSer, bnkSer, altSer, velSer = np.array([thrSer]), np.array([elvSer]), np.array([ailSer]), np.array(
        [pitchSer]), np.array([bnkSer]), np.array([altSer]), np.array([velSer])
    result = model.predict([thrSer, elvSer, ailSer, pitchSer, bnkSer, altSer, velSer])
    return result.tolist()

result=model.predict([thrSer, elvSer, ailSer, pitchSer, bnkSer, altSer, velSer])
# elvSer, pitchSer, bnkSer, altSer, velSer = [.5 for i in range(HISTORY_LENGTH)], [0 for i in range(HISTORY_LENGTH)], [
#    0 for i in range(HISTORY_LENGTH)], [0 for i in range(HISTORY_LENGTH)], [0.7 for i in range(HISTORY_LENGTH)]
thrSer,elvSer, ailSer, pitchSer, bnkSer, altSer, velSer = [], [], [], [], [],[],[]
S = 100
for i in range(HISTORY_LENGTH):
    frame = dataSet[S+STEP*i]
    thrSer.append(frame.rx.thr)
    elvSer.append(frame.rx.elv)
    ailSer.append(frame.rx.ail)
    pitchSer.append(frame.basic.p)
    altSer.append(frame.basic.a)
    velSer.append(frame.basic.s)
    bnkSer.append(frame.basic.b)

while True:
    result = predict(thrSer,elvSer, ailSer, pitchSer, bnkSer, altSer, velSer)[0]
    print(result)
    thrSer.pop(0)
    elvSer.pop(0)
    ailSer.pop(0)
    pitchSer.pop(0)
    bnkSer.pop(0)
    altSer.pop(0)
    velSer.pop(0)
    pitchSer.append(result[0])
    bnkSer.append(result[1])
    altSer.append(result[2])
    velSer.append(result[3])
    thrSer.append(float(input())/10)
    elvSer.append(float(input())/10)
    ailSer.append(float(input())/10)
    for i in range(HISTORY_LENGTH):
        altSer[i] -= result[2]
