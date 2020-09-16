from .readLog import FlightDataSet


def load(STEP, SIZE, dataSet: FlightDataSet, scope="limited"):
    if scope == "limited":
        return __getLimitedSamples(STEP, SIZE, dataSet)
    elif scope == "newStructure":
        return __getPitchElvNewDatastructure(STEP, SIZE, dataSet)
    else:
        return __getAllSamples(STEP, SIZE, dataSet)


def __getLimitedSamples(STEP, SIZE, dataSet: FlightDataSet):
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


def __getPitchElvNewDatastructure(STEP, SIZE, dataSet: FlightDataSet):
    startTime = 0
    inputs, labels = [], []
    while startTime+STEP*SIZE < dataSet.length:
        series = []
        for i in range(0, SIZE):
            frame = dataSet[startTime+i*STEP]
            series.append([frame.basic.p, frame.rx.elv])
        inputs.append(series)
        labels.append([dataSet[startTime+STEP*SIZE].basic.p])
        startTime += 1
    return inputs, labels


def __getAllSamples(STEP, SIZE, dataSet: FlightDataSet):
    startTime = 0
    inputs, labels = [], []
    while startTime+STEP*SIZE < dataSet.length:
        series = []
        lastAlt = dataSet[startTime-STEP].basic.a
        for i in range(0, SIZE):
            frame = dataSet[startTime+i*STEP]
            series.append([frame.basic.p, frame.basic.b, frame.basic.s/10, frame.basic.a-lastAlt,
                           frame.rx.thr, frame.rx.elv, frame.rx.ail])
            lastAlt = frame.basic.a
        inputs.append(series)
        nextFrame = dataSet[startTime+STEP*SIZE]
        labels.append([nextFrame.basic.p, nextFrame.basic.b,
                       nextFrame.basic.s/10, nextFrame.basic.a-lastAlt])
        startTime += 1
    return inputs, labels
    # TF Dataset
    # 0. Dimension Trainingsbeispielindex
    # 1. Dimension Zeit
    # 2. Dimension Parameter
    # pitch, bank, speed, altitude, throttle, elevator, aileron
