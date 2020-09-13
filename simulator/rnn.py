from pathlib import Path
import numpy as np
from helper.tools import constants, readLog, getSamples
import helper.models.rnnSimV2 as sim
import tensorflow as tf
from helper.tools import constants
#model, USE_NEW_DATA_STRUCTURE,cellModel,cell=sim.getCellModel()
model, layer = sim.getCell()
model.compile(
    optimizer=tf.keras.optimizers.Adam(0.0005),
    loss=tf.losses.mse
)
model.summary()

base_path = Path(__file__).parent
file_path = (base_path / "../dataCollection/logs/flight0.txt").resolve()
dataSet = readLog.FlightDataSet(file_path)

SIZE = constants.INPUT_TIME_SERIES_LENGTH
STEP = constants.STEP
inputs, outputs = getSamples.load(STEP, SIZE, dataSet, 'full')
inputs, outputs = np.array(inputs), np.array(outputs)
model.fit(
    x=inputs,
    y=outputs,
    batch_size=50,
    epochs=5
)