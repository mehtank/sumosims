from lxml import objectify
from scipy import interpolate

def interp(x, y, xmax, ydefault=0):
        if len(x) == 0:
            x = [0]
            y = [ydefault]

        newx = []; newy = []

        newindex = x.index(max(x))
        newx.append(x[newindex] - xmax)
        newy.append(y[newindex])

        newindex = x.index(min(x))
        newx.append(x[newindex] + xmax)
        newy.append(y[newindex])

        x.extend(newx); y.extend(newy)

        f = interpolate.interp1d(x, y, assume_sorted=False)
        return f

def parsexml(fn, edgestarts, xmax, ydefault=0):
    obj = objectify.parse(file(fn)).getroot()

    alldata = []
    trng = []
    xrng = range(0, xmax)
    speeds = []
    lanespeeds = {}

    for timestep in obj.timestep:
        t = float(timestep.get("time"))
        this = []
        lanedata = {}
        for edge in timestep.edge:
            for lane in edge.lane:
                lid = lane.get("id")[-1]
                if not lid in lanedata:
                    lanedata[lid] = []
                thislane = []
                try:
                    for vehicle in lane.vehicle:
                        name = vehicle.get("id")
                        v = float(vehicle.get("speed"))
                        x = float(vehicle.get("pos"))+edgestarts[edge.get("id")]
                        thislane.append({"name": name, "time": t, "position": x, "speed": v})
                except AttributeError:
                    pass
                this.extend(thislane)
                lanedata[lid].extend(thislane)
        alldata.extend(this)
        trng.append(t)
        f = interp([x["position"] for x in this], [x["speed"] for x in this], xmax, ydefault)
        speeds.append(f(xrng))
        for lid, thislane in lanedata.iteritems():
            f = interp([x["position"] for x in thislane], [x["speed"] for x in thislane], xmax, ydefault)
            if not lid in lanespeeds:
                lanespeeds[lid] = []
            lanespeeds[lid].append(f(xrng))

    return alldata, trng, xrng, speeds, lanespeeds
