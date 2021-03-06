import inspect
import sys
import os
from pathlib import Path
import importlib
import tensorflow as tf



#load network from simulator folder
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
helperDir = os.path.join(parent_dir, 'simulator')
sys.path.insert(0, helperDir)
from helper.tools import constants
SIZE = constants.INPUT_TIME_SERIES_LENGTH

usedModel = importlib.import_module("helper.models."+constants.MODEL)
simulator:tf.keras.Model = usedModel.getModel(SIZE, constants.PARAMETER_COUNT, constants.PREDICTABLE_PARAM_COUNT)[0]
simulator.load_weights(os.path.join(
    parent_dir, 'simulator', 'checkpoint', constants.MODEL, 'sim')) #load pretrained weights

simulator.trainable = False # prevent simulator from being changed in autopilot training