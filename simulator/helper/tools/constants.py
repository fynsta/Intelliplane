from operator import truediv


INPUT_TIME_SERIES_LENGTH = 25
PARAMETER_COUNT = 5
PREDICTABLE_PARAM_COUNT = 2
CONTROLLABLE_PARAM_COUNT=PARAMETER_COUNT-PREDICTABLE_PARAM_COUNT
STEP = 0.1

MODEL = "rnnSimV2"
LOADBACKUP = True

TRAINING_DATA=["flight0.txt", "flight3.txt"]
