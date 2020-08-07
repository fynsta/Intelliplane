import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
dataSet=['p','b','h','a','s']
dataSets=[]
for var in dataSet:
    dataSets.append([])
timeData = []
base_path = Path(__file__).parent
file_path = (base_path / "../logs/flight1.txt").resolve()
with open(file_path) as json_file:
    data: list = json.load(json_file)
    print(len(data))
    for point in data:
        try:
            newPoint=[]
            for var in dataSet:
                newPoint.append(point[var])
            time: int = point['pcTime']
            for i in range(len(newPoint)):
                dataSets[i].append(newPoint[i])
            timeData.append(time/1000)
        except KeyError:
            p = 0
dataSets[0]*=180/3.1415
for set in dataSets:
    plt.plot(timeData,set)
plt.legend(dataSet)
plt.show()
