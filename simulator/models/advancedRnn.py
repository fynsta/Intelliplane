from tools import readLog
import tensorflow as tf
from ..tools.modelToRnnCell import ModelRnn
layers=tf.keras.layers
def getModel():
    input=layers.Input((INPUT_TIME_SERIES_LENGTH))