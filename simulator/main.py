import tensorflow as tf
from pathlib import Path
import numpy as np

import tools.readLog as t
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
# time, sets = t.readLog(file_path)
dataSet = t.FlightDataSet(file_path)

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

# TODO: Whats the point of the next 3 lines?
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


class ElvPitchModel(tf.keras.Model):
    def __init__(self):
        self.elvLayer = tf.keras.layers.Dense(10)
        self.pitchLayer = tf.keras.layers.Dense(10)
        self.lastLayer = tf.keras.layers.Dense(1)

    """def call(self, elvSer, pitchSer):
        elv = self.elvLayer(elvSer)
        ptch = self.pitchLayer(pitchSer)

        return out"""


def getModel():
    elvIn = tf.keras.layers.Input(shape=(SIZE,))
    pitchIn = tf.keras.layers.Input(shape=(SIZE,))
    #convElv=tf.keras.layers.Conv1D(SIZE-1,5)(elvIn)
    #convPtch=tf.keras.layers.Convolution1D(SIZE,3)(pitchIn)
    elvLayer = tf.keras.layers.Dense(REDSIZE)(elvIn)
    pitchLayer = tf.keras.layers.Dense(REDSIZE)(pitchIn)
    joined = tf.keras.layers.Concatenate()([pitchLayer, elvLayer])
    dense0=tf.keras.layers.Dense(10,'tanh')(joined)
    dense1=tf.keras.layers.Dense(5,'tanh')(dense0)
    outLayer = tf.keras.layers.Dense(units=1)(dense1)
    model = tf.keras.Model(inputs=[elvIn, pitchIn], outputs=outLayer)
    return model


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


# model = ElvPitchModel()
model = getModel()
tf.keras.utils.plot_model(model)
model.summary()
model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss=tf.losses.mse
)
if False:
    xdata, ydata, labels = getSamples()
    # xdata=tf.data.Dataset.from_tensors(xdata)
    # ydata=tf.data.Dataset.from_tensors(ydata)
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    labels = np.array(labels)
    model.fit(
        x=[xdata, ydata],
        y=labels,
        batch_size=50,
        epochs=1000
    )
    model.save_weights('./checkpoint/sim')
    res = model.predict([xdata, ydata], batch_size=50)
    res2=model([xdata,ydata])
    # quit()
else:
    model.load_weights('./checkpoint/sim')


def pred(elv, pitch):
    elv = np.array([elv])
    pitch = np.array([pitch])
    res = model.predict([elv, pitch])
    return np.ndarray.item(res)


pitchSer = [0 for i in range(SIZE)]
elvSer = [0.5 for i in range(SIZE)]
while False:
    next = pred(elvSer, pitchSer)
    print(next)
    pitchSer.pop(0)
    elvSer.pop(0)
    pitchSer.append(next)
    elvSer.append(float(input()))
quit()
def loss(out, tar):
    return tf.reduce_mean(tf.square(out-tar))


optimizer=tf.optimizers.SGD(0.01)


def optimize(pitchSer: tf.Tensor, elvSer: tf.Tensor, target):
    with tf.GradientTape() as t:
        pred=genFrame(pitchSer, elvSer)
        l=loss(pred, target)
    gradients=t.gradient(l, [wElv, wPitch, wTotal])
    optimizer.apply_gradients(zip(gradients, [wElv, wPitch, wTotal]))
    print(l.numpy())


tfData=tfData.shuffle(100)
tfData=tfData.batch(10)
for i in range(0, 10):
    for (pitchSer, elvSer, batch_y) in tfData:
        optimize(pitchSer, elvSer, batch_y)
# for step, (pitchSer, elvSer, batch_y) in enumerate(tfData.take(1000), 1):
#    optimize(pitchSer, elvSer, batch_y)


testPitchSer = tf.zeros([10,10], dtype=tf.float32)
testElvSer = tf.constant([[n/10 for x in range(0, 10)]
                          for n in range(0, 10)], dtype=tf.float32)
print(genFrame(testPitchSer, testElvSer))
