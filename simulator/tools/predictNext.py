import numpy as np

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