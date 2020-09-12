from helper.tools import readLog, constants, predictNext
import trainModel


SIZE = constants.INPUT_TIME_SERIES_LENGTH

model = trainModel.train(constants.LOADBACKUP)
predictNext.predictFromInputNewDataStructure(SIZE, model)
