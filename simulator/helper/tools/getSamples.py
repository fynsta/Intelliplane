from .readLog import FlightDataSet


def load(STEP, SIZE, dataSet: FlightDataSet, scope="limited"):
    """
    load tensorflow-like simulator training dataset from flight log dataset. The type of datastructure to use for the simulator network is specified in "scope"
    "limited" => old, depreciated datastructure
    "newStructure" => only pitch and elevator in new datastructure
    "full" => all supported parameters
    """
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
    # depreciated old datastructure


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
    # TF Dataset
    # 0. Dimension Trainingsbeispielindex
    # 1. Dimension Zeit
    # 2. Dimension Parameter
    # pitch, elevator
    # TF label
    # 0. Dimension Trainingsbeispielindex
    # 1. Dimension Parameter
    # pitch


def __getAllSamples(STEP, SIZE, dataSet: FlightDataSet):
    startTime = 0
    inputs, labels = [], []
    while startTime+STEP*SIZE < dataSet.length:
        series = []
        for i in range(0, SIZE):
            frame = dataSet[startTime+i*STEP]
            series.append([frame.basic.p, frame.basic.b,
                           frame.rx.thr, frame.rx.elv, frame.rx.ail])
        inputs.append(series)
        nextFrame = dataSet[startTime+STEP*SIZE]
        labels.append([nextFrame.basic.p, nextFrame.basic.b, ])
        startTime += 1
    return inputs, labels
    # TF Dataset
    # 0. Dimension Trainingsbeispielindex
    # 1. Dimension Zeit
    # 2. Dimension Parameter
    # pitch, bank (, heading, speed, altitude), throttle, elevator, aileron
    # parameters in brackets are added later
    # TF label
    # 0. Dimension Trainingsbeispielindex
    # 1. Dimension Parameter
    # pitch, bank (, heading, speed, altitude)
