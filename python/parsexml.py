from lxml import objectify
from scipy import interpolate
import numpy as np

def interp(x, y, xmax, vdefault=0):
        if len(x) == 0:
            x = [0]
            y = [vdefault]

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

def parsexml(fn, edgestarts, xmax, vdefault=0):
    obj = objectify.parse(file(fn)).getroot()

    trng = []
    xrng = range(0, xmax)
    lanespeeds = {}
    laneoccupancy = {}
    avgspeeds = {}
    totfuel = {}
    typecolors = {}

    for timestep in obj.timestep:
        t = float(timestep.get("time"))

        lanedata = {}
        try:
            for vehicle in timestep.vehicle:
                d = {}
                d["name"] = vehicle.get("id")
                d["type"] = vehicle.get("id")[:-4]
                d["edge"] = vehicle.get("lane")[:-2]
                d["v"] = float(vehicle.get("speed"))
                d["pos"] = float(vehicle.get("pos"))
                d["x"] = d["pos"] + edgestarts[d["edge"]]

                d["CO2"] = float(vehicle.get("CO2"))
                d["CO"] = float(vehicle.get("CO"))
                d["fuel"] = float(vehicle.get("fuel"))

                lid = vehicle.get("lane")[-1]
                lanedata.setdefault(lid, []).append(d)
        except AttributeError:
            pass

        for lid, thislane in lanedata.iteritems():
            f = interp([x["x"] for x in thislane], [x["v"] for x in thislane], xmax, vdefault)
            types = set([x["type"] for x in thislane])
            for tp in types:
                if tp not in typecolors:
                    typecolors[tp] = len(typecolors)+1

            intx = dict((int(x["x"]), typecolors[x["type"]]) for x in thislane)
            fuel = [x["fuel"] for x in thislane]

            fx = f(xrng)
            lanespeeds.setdefault(lid, [[vdefault]*len(xrng)]*len(trng)).append(fx)
            laneoccupancy.setdefault(lid, [[0]*len(xrng)]*len(trng)).append([intx.get(x, 0) for x in xrng])

            dx = np.diff(np.array(xrng + [xrng[0] + xmax]))
            dt = dx * 1./fx
            avgspeeds.setdefault(lid, [vdefault]*len(trng)).append(np.sum(dx)/np.sum(dt))
            totfuel.setdefault(lid, [vdefault]*len(trng)).append(np.sum(fuel))

        trng.append(t)

    return trng, xrng, avgspeeds, lanespeeds, laneoccupancy, totfuel
