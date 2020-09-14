from curses.ascii import SI
import importlib
import tensorflow as tf
from pathlib import Path
import numpy as np


from helper.tools import constants, readLog, getSamples
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight").resolve()

dataSet = readLog.FlightDataSet(str(file_path)+'0.txt',2)
#for i in range(3,4):
    #dataSet+=readLog.FlightDataSet(str(file_path)+str(i)+'.txt')

usedModel = importlib.import_module("helper.models."+constants.MODEL)

SIZE = constants.INPUT_TIME_SERIES_LENGTH
STEP = constants.STEP


def train(loadBackup: bool):
    model, USE_NEW_DATA_STRUCTURE = usedModel.getModel(
        constants.INPUT_TIME_SERIES_LENGTH, constants.PARAMETER_COUNT, constants.PREDICTABLE_PARAM_COUNT)

    tf.keras.utils.plot_model(model)
    model.summary()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.0002),
        loss=tf.losses.mse
    )

    if loadBackup:
        model.load_weights('./checkpoint/'+constants.MODEL+'/sim')
    else:
        if USE_NEW_DATA_STRUCTURE:
            inputs, outputs = getSamples.load(STEP, SIZE, dataSet, 'full')
            inputs, outputs = np.array(inputs), np.array(outputs)
            model.fit(
                x=inputs,
                y=outputs,
                batch_size=100,
                epochs=2500
            )
        else:
            xdata, ydata, labels = getSamples.load(STEP, SIZE, dataSet)
            xdata = np.array(xdata)
            ydata = np.array(ydata)
            labels = np.array(labels)
            model.fit(
                x=[xdata, ydata],
                y=labels,
                batch_size=150,
                epochs=5000
            )
        model.save_weights('./checkpoint/'+constants.MODEL+'/sim')

    return model
