import tensorflow as tf
import os
from pathlib import Path
import tools.readLog as t
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight1.txt").resolve()
#time, sets = t.readLog(file_path)
dataSet = t.FlightDataSet(file_path)
for el in dataSet:
    print(el.basic.p)

SIZE = 10
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


samples = []
for s in genSample():
    samples.append(s)
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


def loss(out, tar):
    return tf.reduce_mean(tf.square(out-tar))


optimizer = tf.optimizers.SGD(0.01)


def optimize(pitchSer: tf.Tensor, elvSer: tf.Tensor, target):
    with tf.GradientTape() as t:
        pred = genFrame(pitchSer, elvSer)
        l = loss(pred, target)
    gradients = t.gradient(l, [wElv, wPitch, wTotal])
    optimizer.apply_gradients(zip(gradients, [wElv, wPitch, wTotal]))
    print(l.numpy())


tfData = tfData.shuffle(100)
tfData=tfData.batch(10)
for i in range(0,100):
    for (pitchSer, elvSer, batch_y) in tfData:
        optimize(pitchSer, elvSer, batch_y)
#for step, (pitchSer, elvSer, batch_y) in enumerate(tfData.take(1000), 1):
#    optimize(pitchSer, elvSer, batch_y)


testPitchSer = tf.constant([[0.5 for x in range(0, 10)]
                            for n in range(0, 10)], dtype=tf.float32)
testElvSer = tf.constant([[n/10 for x in range(0, 10)]
                          for n in range(0, 10)], dtype=tf.float32)
print(genFrame(testPitchSer, testElvSer))
