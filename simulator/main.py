import tensorflow as tf
from pathlib import Path
import numpy as np

from tools import readLog
import trainModel
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
dataSet = readLog.FlightDataSet(file_path)

SIZE = 20
STEP = 0.1
REDSIZE = 5

model = trainModel.train(True)

def pred(elv, pitch):
    elv = np.array([elv])
    pitch = np.array([pitch])
    res = model.predict([elv, pitch])
    return np.ndarray.item(res)


pitchSer = [0 for i in range(SIZE)]
elvSer = [0.5 for i in range(SIZE)]
while True:
    next = pred(elvSer, pitchSer)
    print(next)
    pitchSer.pop(0)
    elvSer.pop(0)
    pitchSer.append(next)
    elvSer.append(float(input()))
quit()
def loss(out, tar):
    return tf.reduce_mean(tf.square(out-tar))