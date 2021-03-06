import tensorflow as tf
from tensorflow.keras import layers
from getSim import simulator #load pretrained simulator network
from getAp import ap #load trainable autopilot network

from loadStartingPoints import startingPoints,spam, constants #load datasets


simulator.summary()
ap.summary()


def splitParameters(unified: tf.Tensor):
    return tf.split(unified, [constants.PREDICTABLE_PARAM_COUNT, constants.CONTROLABLE_PARAM_COUNT], -1)


def unifyParameters(predictableParameters: tf.Tensor, controllableParameters: tf.Tensor):
    """
    makes a single tensor out of a prediction and a control signal tensor
    """
    return tf.concat([predictableParameters, controllableParameters], -1)


def getApTrainer():
    """
    get the neural network which trains the autopilot. It has a starting situation as input and returns how the situation evolves in the next few timeframes given the simulator and autopilot
    """
    input = layers.Input((None, constants.PARAMETER_COUNT))
    apLayer: layers.RNN = ap.layers[0] #get the rnn layer of the autopilot
    apLayer.return_state = True
    apOutput = apLayer(input) #initialize autopilot state with the starting situation
    apParams = apOutput[0] #also use the computed control signals
    apState = apOutput[1:] #save the state
    simLayer: layers.RNN = simulator.layers[0]#get the rnn layer of the simulator
    simLayer.return_state = True
    simOutput = simLayer(input) #initialize simulator state with the starting situation
    simParams = simOutput[0] #also use the predicted next situation
    simState = simOutput[1:] # save the simultator state
    outputs=[] # list of next situations
    for i in range(20): #predict next 20 situations
        nextInput = unifyParameters(simParams, apParams) #merge simulator and autopilot parameters to new situation
        nextInput=tf.expand_dims(nextInput,axis=1) #make it a time series of length 1
        apOutput = apLayer(nextInput, initial_state=apState) #compute control signals using recovered state
        apParams = apOutput[0]
        apState = apOutput[1:]
        simOutput = simLayer(nextInput, initial_state=simState) #predict next situation using recovered states
        simParams = simOutput[0]
        simState = simOutput[1:]
        outputs.append(tf.expand_dims(simParams,1)) # add predicted situation to time series to return
    outputTensor=layers.concatenate(outputs,1)
    return tf.keras.Model(input,outputTensor)


trainer=getApTrainer()
trainer.summary()
tf.keras.utils.plot_model(trainer, 'rnn_ap.png')

def minimizePitchLoss(y_true,y_pred):
    """
    loss which minimizes pitch and bank values => trained to go straight
    """
    #return tf.reduce_mean(tf.reduce_mean(tf.square(0.1-y_pred[:,:,0]+tf.square(y_pred[:,:,1])+0.01*tf.square(6-y_pred[:,:,2]))))
    return tf.reduce_mean(tf.reduce_mean(tf.square(y_pred)))

trainer.compile(
    optimizer=tf.keras.optimizers.Adam(0.0001),
    loss=minimizePitchLoss
)
if False:
    trainer.fit(
        x=startingPoints,
        y=spam,
        batch_size=200,
        epochs=1500
    )
    trainer.save_weights('./checkpoint/trainer')
else:
    trainer.load_weights('./checkpoint/trainer')
#results=trainer.predict(startingPoints)
#print(results)


#show autopilot behavior in example situation
input=startingPoints[120:121] # take starting situation from training data
apLayer: layers.RNN = ap.layers[0] #predict next situation like in apTrainer
apOutput = apLayer(input)
apParams = apOutput[0]
apState = apOutput[1:]
simLayer: layers.RNN = simulator.layers[0]
simOutput = simLayer(input)
simParams = simOutput[0]
simState = simOutput[1:]

from time import sleep

import matplotlib.pyplot as plt
#initialize plotting tool
LABELS=["pitch","bank","throttle","elevator","aileron"]
#plt.ion()
time=[0.1*i for i in range(25)]
pltValues=list(zip(*list(input[0])))
graphs=[]
for i in range(len(pltValues)):
    graphs.append(plt.plot(time,pltValues[i],label=LABELS[i]))
plt.legend()
for _ in range(70):
    # let autopilot control the situation
    print(simParams.numpy(),'|',apParams.numpy())
    nextInput = unifyParameters(simParams, apParams)
    nextInput=tf.expand_dims(nextInput,axis=1)
    apOutput = apLayer(nextInput, initial_state=apState)
    apParams = apOutput[0]
    apState = apOutput[1:]
    simOutput = simLayer(nextInput, initial_state=simState)
    simParams = simOutput[0]
    simState = simOutput[1:]


    nextVal=list(simParams.numpy()[0])+list(apParams.numpy()[0])
    for i in range(len(pltValues)):
        pltValues[i]+=(nextVal[i],)
    time.append(time[-1]+0.1)
    i=0
    for graph in graphs:
        graph[0].set_xdata(time)
        graph[0].set_ydata(pltValues[i])
        i+=1
    #plt.show()
plt.xlabel("time[s]")
plt.xlim(0,9)
plt.show()
plt.savefig("autopilot_behavior.pdf")