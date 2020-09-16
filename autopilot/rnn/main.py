import tensorflow as tf
from tensorflow.keras import layers
from getSim import simulator
from getAp import ap

from loadStartingPoints import startingPoints,spam, constants


simulator.summary()
ap.summary()


def splitParameters(unified: tf.Tensor):
    return tf.split(unified, [constants.PREDICTABLE_PARAM_COUNT, constants.CONTROLABLE_PARAM_COUNT], -1)


def unifyParameters(predictableParameters: tf.Tensor, controllableParameters: tf.Tensor):
    return tf.concat([predictableParameters, controllableParameters], -1)


def getApTrainer():
    input = layers.Input((None, constants.PARAMETER_COUNT,))
    absoluteHeight=input[:,-1,3]
    apLayer: layers.RNN = ap.layers[0]
    apLayer.return_state = True
    apOutput = apLayer(input)
    apParams = apOutput[0]
    apState = apOutput[1:]
    simLayer: layers.RNN = simulator.layers[0]
    simLayer.return_state = True
    simOutput = simLayer(input)
    simParams = simOutput[0]
    absoluteHeight=absoluteHeight+simParams[:,3]
    simState = simOutput[1:]
    outputs=[]
    for i in range(20):
        nextInput = unifyParameters(simParams, apParams)
        nextInput=tf.expand_dims(nextInput,axis=1)
        apOutput = apLayer(nextInput, initial_state=apState)
        apParams = apOutput[0]
        apState = apOutput[1:]
        simOutput = simLayer(nextInput, initial_state=simState)
        simParams = simOutput[0]
        simState = simOutput[1:]
        outputs.append(tf.expand_dims(simParams,1))
    outputTensor=layers.concatenate(outputs,1)
    return tf.keras.Model(input,outputTensor)


trainer=getApTrainer()
trainer.summary()
tf.keras.utils.plot_model(trainer, 'rnn_ap.png')

def pitchLoss(y_true,y_pred):
    return tf.math.reduce_mean(tf.reduce_mean(tf.square(0.1-y_pred[:,:,0]+tf.square(y_pred[:,:,1])+0.01*tf.square(6-y_pred[:,:,2])), axis=1),axis=0)
    #return tf.reduce_mean(tf.reduce_mean(tf.square(y_pred)))

trainer.compile(
    optimizer=tf.keras.optimizers.Adam(0.0001),
    loss=pitchLoss
)
if True:
    trainer.fit(
        x=startingPoints,
        y=spam,
        batch_size=200,
        epochs=1500
    )
    trainer.save_weights('./checkpoint/trainer')
else:
    trainer.load_weights('./checkpoint/trainer')
results=trainer.predict(startingPoints)
print(results)

input=startingPoints[109:110]
apLayer: layers.RNN = ap.layers[0]
apOutput = apLayer(input)
apParams = apOutput[0]
apState = apOutput[1:]
simLayer: layers.RNN = simulator.layers[0]
simOutput = simLayer(input)
simParams = simOutput[0]
simState = simOutput[1:]


while True:
    print(simParams.numpy(),'|',apParams.numpy())
    nextInput = unifyParameters(simParams, apParams)
    nextInput=tf.expand_dims(nextInput,axis=1)
    apOutput = apLayer(nextInput, initial_state=apState)
    apParams = apOutput[0]
    apState = apOutput[1:]
    simOutput = simLayer(nextInput, initial_state=simState)
    simParams = simOutput[0]
    simState = simOutput[1:]