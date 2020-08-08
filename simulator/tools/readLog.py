import json
import inspect
VARNAMES = ['p', 'b', 'h', 'a', 's']
RXVARS = ['thr', 'ail', 'elv']
GPSVARS = ['lat', 'lon', 'gpsTime']


class Frame:
    def __init__(self, map):
        self.time = map['pcTime']/1000


class BasicFrame(Frame):
    def __init__(self, map: map):
        super().__init__(map)
        self.p = map['p']
        self.b = map['b']
        self.h = map['h']
        self.a = map['a']
        self.s = map['s']


class RXFrame(Frame):
    def __init__(self, map: map):
        super().__init__(map)
        self.thr = map['thr']
        self.elv = map['ail']
        self.ail = map['elv']


class GPSFrame(Frame):
    def __init__(self, map: map):
        super().__init__(map)
        self.lat = map['lat']
        self.lon = map['lon']
class TotalDataSet:
    def __init__(self,basic,rx,gps):
        self.basic=basic
        self.rx=rx
        self.gps=gps

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

    def __getitem__(self, time):
        time+=self.startTime
        mi=0
        ma=len(self.data)-1
        while mi+1<ma:
            av=round((mi+ma)/2)
            if self.data[av].time<time:
                mi=av
            else:
                ma=av
        basic=True
        rx=True
        gps=True
        basicD=0
        rxD=0
        gpsD=0
        while (basic or rx or gps) and av+1<len(self.data):
            if isinstance(self.data[av],BasicFrame):
                basicD=self.data[av]
                basic=False
            if isinstance(self.data[av],RXFrame):
                rx=False
                rxD=self.data[av]
            if isinstance(self.data[av],GPSFrame):
                gps=False
                gpsD=self.data[av]
            av+=1
        return TotalDataSet(basicD,rxD,gpsD)


def readLog(path):
    dataSets = []
    for var in VARNAMES:
        dataSets.append([])
    timeData = []
    print('reading log')
    with open(path) as json_file:
        data: list = json.load(json_file)
        print(len(data))
        for point in data:
            try:
                newPoint = []
                for var in VARNAMES:
                    newPoint.append(point[var])
                time: int = point['pcTime']
                for i in range(len(newPoint)):
                    dataSets[i].append(newPoint[i])
                timeData.append(time/1000)
            except KeyError:
                pass
            try:
                newPoint = []
                for var in RXVARS:
                    newPoint.append(point[var])
                time: int = point['pcTime']
                for i in range(len(newPoint)):
                    dataSets[i].append(newPoint[i])
            except KeyError:
                pass
    return timeData, dataSets
