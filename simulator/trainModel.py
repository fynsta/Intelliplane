from curses.ascii import SI
from helper.tools.constants import TRAINING_DATA
import importlib
import tensorflow as tf
from pathlib import Path
import numpy as np


#get dataset when module is loaded
from helper.tools import constants, readLog, getSamples
base_path = Path(__file__).parent

dataSet = readLog.FlightDataSet(str((base_path / ("../dataCollection/logs/"+constants.TRAINING_DATA[0])).resolve()),2) #get dataset from first flight path
for i in range(1,len(constants.TRAINING_DATA)):
    dataSet+=readLog.FlightDataSet(str((base_path / ("../dataCollection/logs/"+constants.TRAINING_DATA[i])).resolve()),2) #merge additional flights into dataset

usedModel = importlib.import_module("helper.models."+constants.MODEL) #load neural network



def train(loadBackup: bool=False):
    """
    get trained simulator model. If specified load pretrained weights
    """

    #load neural network and the type of datastructure it uses
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
        #get tensorflow dataset and train model
        if USE_NEW_DATA_STRUCTURE:
            #get raining examples from flight log dataset
            inputs, outputs = getSamples.load(constants.STEP, constants.INPUT_TIME_SERIES_LENGTH, dataSet, 'full')
            inputs, outputs = np.array(inputs), np.array(outputs)
            model.fit(
                x=inputs,
                y=outputs,
                batch_size=100,
                epochs=2500
            )
        else:
            #get raining examples from flight log dataset
            xdata, ydata, labels = getSamples.load(constants.STEP, constants.INPUT_TIME_SERIES_LENGTH, dataSet)
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
