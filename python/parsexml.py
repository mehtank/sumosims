from lxml import objectify
from scipy import interpolate
import numpy as np

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
    lanespeeds = {}
    laneoccupancy = {}
    avgspeeds = {}

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

        for lid, thislane in lanedata.iteritems():
            f = interp([x["position"] for x in thislane], [x["speed"] for x in thislane], xmax, ydefault)
            intx = [int(x["position"]) for x in thislane]

            if not lid in lanespeeds:
                lanespeeds[lid] = []
            if not lid in laneoccupancy:
                laneoccupancy[lid] = []

            lanespeeds[lid].append(f(xrng))
            laneoccupancy[lid].append([1 if x in intx else 0 for x in xrng])

    for lid, speeds in lanespeeds.iteritems():
        dx = np.diff(np.array(xrng + [xrng[0] + xmax]))
        dt = dx * 1./np.array(speeds)
        avgspeeds[lid] = np.sum(dx)/np.sum(dt, axis=1)

    return trng, xrng, avgspeeds, lanespeeds, laneoccupancy
