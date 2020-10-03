#this is the init point for training the autopilot

from helper.tools import constants, predictNext
import trainModel



#load trained model
model = trainModel.train(constants.LOADBACKUP)

#start interactive simulator
predictNext.predictFromInputNewDataStructure(constants.INPUT_TIME_SERIES_LENGTH, model)