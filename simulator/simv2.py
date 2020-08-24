import tensorflow as tf
from pathlib import Path
import numpy as np

import tools.readLog as t
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
# time, sets = t.readLog(file_path)
dataSet = t.FlightDataSet(file_path)