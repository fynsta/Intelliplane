import helper.models.rnnSimV2 as sim
import tensorflow as tf
from helper.tools import constants
#model, USE_NEW_DATA_STRUCTURE,cellModel,cell=sim.getCellModel()
model,cell=sim.getCell()
model.summary()