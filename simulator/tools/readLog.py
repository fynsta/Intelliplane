import json
import copy
VARNAMES = ['p', 'b', 'h', 'a', 's']
RXVARS = ['thr', 'ail', 'elv']
GPSVARS = ['lat', 'lon', 'gpsTime']


class Frame:
    def __init__(self, map):
        self.time = map['pcTime']/1000

    def add(self, b, factor):
        self.time += factor*(b.time-self.time)


class BasicFrame(Frame):
    def __init__(self, map: map):
        super().__init__(map)
        self.p = map['p']
        self.b = map['b']
        self.h = map['h']
        self.a = map['a']
        self.s = map['s']

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
        self.thr = map['thr']
        self.elv = map['ail']
        self.ail = map['elv']

    def add(self, b, factor):
        super().add(b, factor)
        self.thr += factor*(b.thr-self.thr)
        self.elv += factor*(b.elv-self.elv)
        self.ail += factor*(b.ail-self.ail)


class GPSFrame(Frame):
    def __init__(self, map: map):
        super().__init__(map)
        self.lat = map['lat']
        self.lon = map['lon']

    def add(self, b, factor):
        super().add(b, factor)
        self.lat += factor*(b.lat-self.lat)
        self.lon += factor*(b.lon-self.lon)


class TotalDataSet:
    def __init__(self, basic:BasicFrame, rx:RXFrame, gps:GPSFrame):
        self.basic = basic
        self.rx = rx
        self.gps = gps


class FlightDataSet:
    def __init__(self, path):
        self.data = []
        with open(path) as json_file:
            data: list = json.load(json_file)
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
        self.startTime = self.data[0].time
        self.length = self.data[len(self.data)-1].time-self.startTime

    def __getitem__(self, time):
        time += self.startTime
        mi = 0
        ma = len(self.data)-1
        while mi+1 < ma:
            av = round((mi+ma)/2)
            if self.data[av].time < time:
                mi = av
            else:
                ma = av
        f1, f2 = self.findFrames(av, BasicFrame)
        basic = self.weighFrames(f1, f2, time)
        f1, f2 = self.findFrames(av, RXFrame)
        rx = self.weighFrames(f1, f2, time)
        f1, f2 = self.findFrames(av, GPSFrame)
        gps = self.weighFrames(f1, f2, time)
        return TotalDataSet(basic, rx, gps)

    def findFrames(self, startIndex: int, frameType: type):
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

    def weighFrames(self, f1: Frame, f2: Frame, time):
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
