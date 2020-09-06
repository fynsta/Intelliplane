def load(STEP, SIZE, dataSet, scope="limited"):
    if scope == "limited":
        return __getLimitedSamples(STEP, SIZE, dataSet)
    else:
        return __getAllSamples(STEP, SIZE, dataSet)

def __getLimitedSamples(STEP, SIZE, dataSet):
    startTime = 0
    pitchSer = []
    elvSer = []
    labels = []
    while startTime+STEP*SIZE < dataSet.length:
        elvFrame = []
        pitchFrame = []
        for i in range(0, SIZE):
            frame = dataSet[startTime+i*STEP]
            elvFrame.append(frame.rx.elv)
            pitchFrame.append(frame.basic.p)
        pitchSer.append(pitchFrame)
        elvSer.append(elvFrame)
        labels.append(dataSet[startTime+STEP*SIZE].basic.p)
        startTime += 1
    return elvSer, pitchSer, labels

def __getAllSamples(STEP, SIZE, dataSet):
    startTime = 0
    pitchSer = []
    elvSer = []
    labels = []
    while startTime+STEP*SIZE < dataSet.length:
        elvFrame = []
        pitchFrame = []
        for i in range(0, SIZE):
            frame = dataSet[startTime+i*STEP]
            elvFrame.append(frame.rx.elv)
            pitchFrame.append(frame.basic.p)
        pitchSer.append(pitchFrame)
        elvSer.append(elvFrame)
        labels.append(dataSet[startTime+STEP*SIZE].basic.p)
        startTime += 1
    return elvSer, pitchSer, labels