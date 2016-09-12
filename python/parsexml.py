from lxml import objectify
from scipy import interpolate

def interp(x, y, xmax):
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

def parsexml(fn, edgestarts, xmax):
    obj = objectify.parse(file(fn)).getroot()

    alldata = []
    trng = []
    xrng = range(0, xmax)
    speeds = []

    for timestep in obj.timestep:
        t = float(timestep.get("time"))
        this = []
        for edge in timestep.edge:
            for lane in edge.lane:
                try:
                    for vehicle in lane.vehicle:
                        name = vehicle.get("id")
                        v = float(vehicle.get("speed"))
                        x = float(vehicle.get("pos"))+edgestarts[edge.get("id")]
                        this.append({"name": name, "time": t, "position": x, "speed": v})
                except AttributeError:
                    pass
        alldata.extend(this)
        trng.append(t)
        f = interp([x["position"] for x in this], [x["speed"] for x in this], xmax)
        speeds.append(f(xrng))
    return alldata, trng, xrng, speeds
