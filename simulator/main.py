from pathlib import Path
from tools import readLog, constants, predictNext
import trainModel

base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight2.txt").resolve()
dataSet = readLog.FlightDataSet(file_path)

SIZE = constants.INPUT_TIME_SERIES_LENGTH

model = trainModel.train(True)
predictNext.predictFromInput(SIZE, model)
