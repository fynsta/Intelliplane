from helper.models import basicModel as usedModel
import tensorflow as tf
from pathlib import Path
import numpy as np

from helper.tools import constants, readLog, getSamples
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
dataSet = readLog.FlightDataSet(file_path)

SIZE = constants.INPUT_TIME_SERIES_LENGTH
STEP = constants.STEP


def train(loadBackup):
    model = usedModel.getModel(SIZE)

    tf.keras.utils.plot_model(model)
    model.summary()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.losses.mse
    )

    if loadBackup:
        model.load_weights('./checkpoint/sim')
    else:
        xdata, ydata, labels = getSamples.load(STEP, SIZE, dataSet)
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

    return model
