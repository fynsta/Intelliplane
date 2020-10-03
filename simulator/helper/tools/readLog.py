import json
import copy
VARNAMES = ['p', 'b', 'h', 'a', 's']
RXVARS = ['thr', 'ail', 'elv']
GPSVARS = ['lat', 'lon', 'gpsTime']


class Frame:
    """
    Base class for all data frames. All frames have a time. See https://en.wikipedia.org/wiki/Aircraft_principal_axes for deatiled explaination of subclass parameters.
    """

    def __init__(self, map: map):
        self.time: float = map['pcTime']/1000

    def add(self, b, factor):
        self.time += factor*(b.time-self.time)


class BasicFrame(Frame):
    def __init__(self, map: map):
        super().__init__(map)
        self.p: float = map['p']  # pitch in radians
        self.b: float = map['b']  # bank in radians
        self.h: float = map['h']  # heading in radians
        self.a: float = map['a']  # altitude above sea level in meters
        self.s: float = map['s']  # speed in m/s

    def add(self, b, factor):
        super().add(b, factor)
        self.p += factor*(b.p-self.p)
        self.b += factor*(b.b-self.b)
        self.h += factor*(b.h-self.h)
        self.a += factor*(b.a-self.a)
        self.s += factor*(b.s-self.s)


class RXFrame(Frame):
    def __init__(self, map: map):
        super().__init__(map)
        self.thr: float = map['thr']  # throttle value (0=^off, 1=^ full power)
        # elevator value(0=^ full down, 1=^ full up)
        self.elv: float = map['elv']
        # aileron value(0=^full right, 1=^ full left)
        self.ail: float = map['ail']

    def add(self, b, factor):
        super().add(b, factor)
        self.thr += factor*(b.thr-self.thr)
        self.elv += factor*(b.elv-self.elv)
        self.ail += factor*(b.ail-self.ail)


class GPSFrame(Frame):
    def __init__(self, map: map):
        super().__init__(map)
        self.lat: float = map['lat']  # latitude in degrees
        self.lon: float = map['lon']  # longitude in degrees

    def add(self, b, factor):
        super().add(b, factor)
        self.lat += factor*(b.lat-self.lat)
        self.lon += factor*(b.lon-self.lon)


class TotalFrame:
    def __init__(self, basic: BasicFrame, rx: RXFrame, gps: GPSFrame):
        self.basic = basic
        self.rx = rx
        self.gps = gps


class DataSetIterator:
    def __init__(self, set):
        self.set = set
        self.index = 0

    def __next__(self):
        if self.index < self.set.length:
            self.index += 1
            return self.set[self.index]
        else:
            raise StopIteration


class FlightDataSet:
    """
    Dataset python class which saves a flight log file and exposes a method to get all parameters at a given time
    """

    def __init__(self, path, speedCut=2):
        self.data = []
        with open(path) as json_file:
            data: list = json.load(json_file)
            print(data[0])
            for point in data:
                f = 0
                try:
                    f = BasicFrame(point)
                except KeyError:
                    pass
                try:
                    f = RXFrame(point)
                except KeyError:
                    pass
                try:
                    f = GPSFrame(point)
                except KeyError:
                    pass
                if f != 0:
                    self.data.append(f)
        while True:
            frame = self.data[0]
            if isinstance(frame, BasicFrame) and frame.s > speedCut:
                break
            else:
                self.data.pop(0)
        while True:
            frame = self.data[-1]
            if isinstance(frame, BasicFrame) and frame.s > speedCut:
                break
            else:
                self.data.pop(-1)
        self.startTime = self.data[0].time
        self.length = self.data[-1].time-self.startTime

        basicFrames = list(
            filter(lambda frame: isinstance(frame, BasicFrame), self.data))
        newSpeedValues = []
        lastChange = 0
        lastValue = 0
        for index, frame in enumerate(basicFrames):
            if frame.s != lastValue:
                newSpeedValues.append((lastChange, lastValue))
                lastChange = index
                lastValue = frame.s
        last = newSpeedValues[0]
        for startIndex, value in newSpeedValues:
            length = -last[0]+startIndex
            if length == 0:
                continue
            delta = value-last[1]
            for i in range(last[0], startIndex):
                basicFrames[i].s = last[1]+(i-last[0])/length*delta
            last = (startIndex, value)

    def __getitem__(self, time):
        """
        get all parameters at time from recording start in seconds. It uses a linear interpolation between the nearest recorded frames
        """
        time += self.startTime
        mi = 0
        ma = len(self.data)-1
        while mi+1 < ma:
            av = round((mi+ma)/2)
            if self.data[av].time < time:
                mi = av
            else:
                ma = av
        f1, f2 = self._findFrames(av, BasicFrame)
        basic = self._weighFrames(f1, f2, time)
        f1, f2 = self._findFrames(av, RXFrame)
        rx = self._weighFrames(f1, f2, time)
        f1, f2 = self._findFrames(av, GPSFrame)
        gps = self._weighFrames(f1, f2, time)
        return TotalFrame(basic, rx, gps)

    def _findFrames(self, startIndex: int, frameType: type):
        """
        get frames of given type which have smaller or bigger time value than the one at start index
        """
        minIndex = startIndex
        minFrame: frameType = None
        while minIndex > 0:
            if isinstance(self.data[minIndex], frameType):
                minFrame = self.data[minIndex]
                break
            minIndex -= 1

        maxIndex = startIndex
        maxFrame: frameType = None
        while maxIndex+1 < len(self.data):
            if isinstance(self.data[maxIndex], frameType):
                maxFrame = self.data[maxIndex]
                break
            maxIndex += 1
        return minFrame, maxFrame

    def _weighFrames(self, f1: Frame, f2: Frame, time):
        """
        interpolate linearly between two frames to get frame at "time"
        """
        if f1 == None:
            return f2
        if f2 == None:
            return f1
        if f1.time == f2.time:
            return f1
        factor = (time-f1.time)/(f2.time-f1.time)
        toReturn = copy.deepcopy(f1)
        toReturn.add(f2, factor)
        return toReturn

    def __iter__(self):
        return DataSetIterator(self)

    def __iadd__(self, other):
        """
        append other dataset to self
        """
        for frame in other.data:
            frame.time += self.length+self.startTime-other.startTime+0.5
            self.data.append(frame)
        self.length += other.length
        return self
