import os
from pathlib import Path
import tools.readLog as t
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight1.txt").resolve()
#time, sets = t.readLog(file_path)
dataSet = t.FlightDataSet(file_path)
p = dataSet[10]
print(p)
