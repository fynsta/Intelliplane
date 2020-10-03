import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


def predictFromInput(SIZE, model):
    pitchSer = [0 for i in range(SIZE)]
    elvSer = [0.5 for i in range(SIZE)]
    while True:
        next = predict(elvSer, pitchSer, model)
        print(next)
        pitchSer.pop(0)
        elvSer.pop(0)
        pitchSer.append(next)
        elvSer.append(float(input()))


def predict(elv, pitch, model):
    elv = np.array([elv])
    pitch = np.array([pitch])
    res = model.predict([elv, pitch])
    return np.ndarray.item(res)


def predictFromInputNewDataStructure(SIZE, simulatorModel: tf.keras.Model):
    """
    let user input control values and simulate next state using simulator. The input is in the form "throttle", "elevator", "pitch", each in a new line. The output has the shape ["pitch", "bank"]
    """
    LABELS=["pitch","bank","throttle","elevator","aileron"]
    history = [[0, 0, 0.5, 0.5, 0.5] for i in range(SIZE)]
    plt.ion()
    time=[0.1*i for i in range(SIZE)]
    pltValues=list(zip(*history))
    graphs=[]
    for i in range(len(pltValues)):
        graphs.append(plt.plot(time,pltValues[i],label=LABELS[i]))
    plt.legend()
    plt.draw()
    counter=0
    while True:
        res = simulatorModel.predict(np.array([history]))
        next = res.tolist()[0]
        print(next)
        history.pop(0)
        history.append(next+[float(input()),float(input()),float(input())])


        #draw new values
        for i in range(len(pltValues)):
            pltValues[i]+=(history[-1][i],)
        time.append(time[-1]+0.1)
        i=0
        for graph in graphs:
            graph[0].set_xdata(time)
            graph[0].set_ydata(pltValues[i])
            i+=1
        plt.draw()