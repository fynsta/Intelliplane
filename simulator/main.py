import os
from pathlib import Path
import tools.readLog as t
base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight1.txt").resolve()
#time, sets = t.readLog(file_path)
dataSet = t.FlightDataSet(file_path)

t = 0
while t < dataSet.length:
    print(t,':',dataSet[t].basic.a)
    t+=0.1
