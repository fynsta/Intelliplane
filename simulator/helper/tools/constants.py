


INPUT_TIME_SERIES_LENGTH = 25 #length of history to predict from
PARAMETER_COUNT = 5 # total number of controllable and measurable parameters
PREDICTABLE_PARAM_COUNT = 2 #not controllable parameters (pitch, bank)
CONTROLLABLE_PARAM_COUNT=PARAMETER_COUNT-PREDICTABLE_PARAM_COUNT #controllable parameters (throttle, elevator, aileron)
STEP = 0.1 #timesteps to predict in seconds.

MODEL = "rnnSimV2" #the only 100% working model by now
LOADBACKUP = True # whether to load a pretrained model or not

TRAINING_DATA=["flight0.txt", "flight3.txt"] #flight logs to use
