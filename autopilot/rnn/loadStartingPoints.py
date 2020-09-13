import inspect
import sys
import os
from pathlib import Path
import importlib
import numpy as np
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
helperDir = os.path.join(parent_dir, 'simulator')
sys.path.insert(0, helperDir)

base_path = Path(__file__).parent.parent
file_path = (base_path / "../dataCollection/logs/flight0.txt").resolve()
from helper.tools import readLog, getSamples, constants
dataSet = readLog.FlightDataSet(file_path)
SIZE = constants.INPUT_TIME_SERIES_LENGTH
startingPoints, spam = getSamples.load(constants.STEP, SIZE, dataSet,'full')
startingPoints = np.array(startingPoints)
spam = np.array(spam)