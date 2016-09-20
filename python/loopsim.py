import subprocess
import sys
import os
import errno
import random
import copy
import numpy as np

# Make sure $SUMO_HOME/tools is in $PYTHONPATH
from sumolib import checkBinary
import traci
import traci.constants as tc

import config as defaults
from makecirc import makecirc, makenet
from parsexml import parsexml
from plots import pcolor, pcolor_multi


KNOWN_PARAMS = {
        "maxSpeed"      : traci.vehicletype.setMaxSpeed,
        "accel"         : traci.vehicletype.setAccel,
        "decel"         : traci.vehicletype.setDecel,
        "sigma"         : traci.vehicletype.setImperfection,
        "tau"           : traci.vehicletype.setTau,
        "speedFactor"   : traci.vehicletype.setSpeedFactor,
        "speedDev"      : traci.vehicletype.setSpeedDeviation,
        "shape"         : traci.vehicletype.setShapeClass,
        }

if defaults.RANDOM_SEED:
    print "Setting random seed to ", defaults.RANDOM_SEED
    random.seed(defaults.RANDOM_SEED)

def ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    return path

class LoopSim:

    def __init__(self, name, length, numLanes, 
            simStepLength=defaults.SIM_STEP_LENGTH,
            speedLimit=defaults.SPEED_LIMIT, port=defaults.PORT):
        self.name = "%s-%dm%dl" % (name, length, numLanes)
        self.length = length
        self.numLanes = numLanes
        self.speedLimit = speedLimit
        self.simStepLength = simStepLength

        edgelen = length/4.
        self.edgestarts = {"bottom": 0, 
                           "right": edgelen, 
                           "top": 2*edgelen, 
                           "left": 3*edgelen}

        self._mkdirs(name)
        # Make loop network
        self.netfn = makenet(self.name, 
                length=self.length, 
                lanes=self.numLanes,
                speedLimit=speedLimit,
                path=self.net_path)
        self.port = port

    def _mkdirs(self, name):
        self.net_path = ensure_dir("%s" % defaults.NET_PATH)
        self.data_path = ensure_dir("%s" % defaults.DATA_PATH)
        self.img_path = ensure_dir("%s" % defaults.IMG_PATH)
        self.vid_path = ensure_dir("%s" % defaults.VID_PATH)

    def _simInit(self, typeList, sumo, sublane):
        self.cfgfn, self.outs = makecirc(self.name+"-"+self.label, 
                netfn=self.netfn, 
                numcars=0, 
                typelist=typeList,
                dataprefix = defaults.DATA_PATH)

        # Start simulator
        sumoBinary = checkBinary(sumo)
        sumoProcessArgs = [
                sumoBinary, 
                "--step-length", repr(self.simStepLength),
                "--no-step-log",
                "-c", self.cfgfn,
                "--remote-port", str(self.port)]
        if sublane:
            sumoProcessArgs.extend(["--lateral-resolution", "5"])
        self.sumoProcess = subprocess.Popen(sumoProcessArgs,
            stdout=sys.stdout, stderr=sys.stderr)

        # Initialize TraCI
        traci.init(self.port)

    def _getEdge(self, x):
        for (e, s) in self.edgestarts.iteritems():
            if x >= s:
                starte = e
                startx = x-s
        return starte, startx

    def _getX(self, edge, position):
        return position + self.edgestarts[edge]

    def _addTypes(self, paramsList):
        self.maxSpeed = 0
        self.carFns = {}

        for params in paramsList:
            name = params["name"]
            self.carFns[name] = params.get("function", None)
            maxSpeed = params.get("maxSpeed", defaults.SPEED_LIMIT)

            for (pname, pvalue) in params.iteritems():
                if pname in KNOWN_PARAMS:
                    KNOWN_PARAMS[pname](name, pvalue)

            self.maxSpeed = max(self.maxSpeed, maxSpeed)

    def _createCar(self, name, x, vtype, lane):
        starte, startx = self._getEdge(x)
        traci.vehicle.addFull(name, "route"+starte, typeID=vtype)
        traci.vehicle.moveTo(name, starte + "_" + repr(lane), startx)

    def _addCars(self, paramsList):
        cars = {}
        self.numCars = 0

        # Tabulate total number of cars per lane
        num_cars_per_lane = [0] * self.numLanes

        # Create car list
        for param in paramsList:
            self.numCars += param["count"]
            for i in range(param["count"]):
                vtype = param["name"]
                laneSpread = param.get("laneSpread", True)
                if laneSpread is not True:
                    num_cars_per_lane[laneSpread] += 1
                carname = "%s-%03d" % (vtype, i)
                cars[carname] = (vtype, laneSpread)

        lane = -1
        carsitems = cars.items()

        # Add all cars to simulation ...
        random.shuffle(carsitems)  # randomly

        # Counters of cars added so far (per lane)
        cars_added_per_lane = [0] * self.numLanes
        # For lanespead = True, set the default cars per lane
        default_cars_per_lane = np.ceil(float(self.numCars) / self.numLanes)

        for carname, (vtype, laneSpread) in carsitems:
            if laneSpread is True:
                # If lanespread = True, then uniformly set the car positions
                lane = (lane + 1) % self.numLanes
                lane_total = default_cars_per_lane
            else:
                # Otherwise, space the cars out evenly per lane
                lane = laneSpread
                lane_total = num_cars_per_lane[laneSpread]

            x = self.length * cars_added_per_lane[lane] / lane_total
            cars_added_per_lane[lane] += 1
            self._createCar(carname, x, vtype, lane)

        self.carNames = cars.keys()

    def _setCarColor(self, car, speedRange):
        if speedRange is None:
            mn, mx = 0, self.maxSpeed
        else:
            mn, mx = speedRange
        dv5 = (mx-mn)/5.

        v = car["v"]
        if v < mn:
            # blue because black doesn't show up against the road
            color = (0,0,255,0) 
        elif v < mn + dv5:
            # blue to red
            color = (255.*(v-mn)/dv5, 0, 255.*(mn+dv5-v)/dv5, 0)
        elif v < mn + 3*dv5:
            # red to yellow
            color = (255, 255.*(v-mn-dv5)/(2*dv5), 0, 0)
        elif v < mx:
            # yellow to green
            color = (255.*(mx-v)/(2*dv5), 255, 0, 0)
        else:
            # green
            color = (0, 255, 0, 0)

        traci.vehicle.setColor(car["id"], color)

    def _run(self, simSteps, speedRange, sumo):
        vid_path = ensure_dir("%s/%s" % (self.vid_path, self.name+"-"+self.label))
        for step in range(simSteps):
            traci.simulationStep()
            self.allCars = []
            for v in self.carNames:
                car = {}
                car["id"] = v
                car["type"] = traci.vehicle.getTypeID(v)
                car["edge"] = traci.vehicle.getRoadID(v)
                position = traci.vehicle.getLanePosition(v)
                car["lane"] = traci.vehicle.getLaneIndex(v)
                car["x"] = self._getX(car["edge"], position)
                car["v"] = traci.vehicle.getSpeed(v)
                car["maxv"] = traci.vehicle.getMaxSpeed(v)
                car["f"] = traci.vehicle.getSpeedFactor(v)
                self.allCars.append(car)
            self.allCars.sort(key=lambda x: x["x"])

            for (idx, car) in enumerate(self.allCars):
                self._setCarColor(car, speedRange)
                carFn = self.carFns[car["type"]]
                if carFn is not None:
                    carFn((idx, car), self, step)
            if sumo == "sumo-gui":
                # Save a frame of the gui output to file 
                # Combine all frames to make a video animation of sim results
                traci.gui.screenshot("View #0", "%s/%08d.png" % (vid_path, step))

        traci.close()
        sys.stdout.flush()
        self.sumoProcess.wait()

    def getCars(self, idx, numBack = None, numForward = None, 
                           dxBack = None, dxForward = None,
                           lane = None):
        ret = []
        x = self.allCars[idx]["x"]

        for i in range(idx-1, -1, -1) + range(self.numCars-1, idx, -1):
            c = self.allCars[i]
            if (dxBack is not None and (x - c["x"]) % self.length > dxBack) or \
               (numBack is not None and len(ret) >= numBack):
                    break
            if (lane is None or c["lane"] == lane):
                    ret.insert(0, c)

        cnt = len(ret)

        for i in range(idx+1, self.numCars) + range(0, idx):
            c = self.allCars[i]
            if (dxForward is not None and (c["x"]-x) % self.length > dxForward) or \
               (numForward is not None and (len(ret) - cnt) >= numForward):
                    break
            if (lane is None or c["lane"] == lane):
                    ret.append(c)

        return ret


    def simulate(self, opts, sumo=defaults.BINARY, speedRange=None, sublane=False):

        self.label = opts.get("label", None)
        tag = opts.get("tag", None)

        paramsList = opts["paramsList"]
        self.simSteps = opts.get("simSteps", 500)

        if self.label is None:
            self.label = "-".join([x["name"] + "%03d" % x["count"] 
                                        for x in paramsList])
        if tag is not None:
            self.label += "-" + tag

        self._simInit([x["name"] for x in paramsList], sumo, sublane)
        self._addTypes(paramsList)
        self._addCars(paramsList)
        self._run(self.simSteps, speedRange, sumo)

    def plot(self, show=True, save=False, speedRange=None, fuelRange=None):
        # Plot results
        emfn = self.outs["emission"]
        trng, xrng, avgspeeds, lanespeeds, (laneoccupancy, typecolors), totfuel, looptimes = parsexml(emfn, self.edgestarts, self.length, self.speedLimit)

        if speedRange == 'avg':
            mnspeed = min([min(s) for s in avgspeeds.values()])
            mxspeed = max([max(s) for s in avgspeeds.values()])
        elif speedRange == 'tight':
            mnspeed = min([np.percentile(s,5) for s in avgspeeds.values()])
            mxspeed = max([np.percentile(s,95) for s in avgspeeds.values()])
        elif speedRange == 'road':
            mnspeed, mxspeed = 0, self.speedLimit
        elif speedRange is None or speedRange == 'car':
            mnspeed, mxspeed = 0, self.maxSpeed
        else:
            mnspeed, mxspeed = speedRange

        if fuelRange == 'avg':
            mnfuel = min([min(s) for s in avgfuels.values()])
            mxfuel = max([max(s) for s in avgfuels.values()])
        elif fuelRange == 'tight':
            mnfuel = min([np.percentile(s,5) for s in avgfuels.values()])
            mxfuel = max([np.percentile(s,95) for s in avgfuels.values()])
        elif fuelRange is None or fuelRange == 'car':
            mnfuel, mxfuel = None, None
        else:
            mnfuel, mxfuel = fuelRange

        print "Generating interpolated plot..."
        plt = pcolor_multi("Traffic jams (%d lanes, %s)" % (self.numLanes, self.label), 
                (xrng, "Position along loop (m)"),
                (trng, "Time (s)"),
                (avgspeeds, "Average loop speed (m/s)"),
                (lanespeeds, mnspeed, mxspeed, "Speed (m/s)"),
                (looptimes, "Loop transit time (s)"),
                (totfuel, mnfuel, mxfuel, "Speed std. dev. (m/s)"))

        fig = plt.gcf()
        if show:
            plt.show()
        if save:
            fig.savefig(defaults.IMG_PATH + self.name + "-" + self.label + ".png")
        return plt

# this is the main entry point of this script
if __name__ == "__main__":
    from carfns import randomChangeLaneFn, ACCFnBuilder, changeFasterLaneBuilder, MidpointFnBuilder, SwitchVTypeFn

    changeFasterLane = changeFasterLaneBuilder()
    # changeFasterLane = changeFasterLaneBuilder(likelihood=1, speedThreshold=2)
    humanParams = {
        "name"        : "human",
        "count"       :  25,
        "maxSpeed"    :  40,
        "accel"       :   2.6,
        "decel"       :   4.5,
        # "function"    : randomChangeLaneFn,
        "function"  : changeFasterLane,
        "laneSpread"  : 0,
        "speedFactor" : 1.1,
        "speedDev"    : 0.5,
        "sigma"       : 0.75,
        "tau"         : 3, # http://www.croberts.com/respon.htm
        # "laneChangeModel": 'LC2013',
    }

    robotParams = {
        "name"        : "robot",
        "count"       :  0,
        "maxSpeed"    :  40,
        "accel"       :   4,
        "decel"       :   6,
        # "function"    : MidpointFnBuilder(max_speed=40, gain=0.1, beta=0.9, duration=250, bias=1.0, ratio=0.25),
        "function"    : ACCFnBuilder(follow_sec=1.0, max_speed=40, gain=0.1, beta=0.9),
        "laneSpread"  : 0,
        "tau"         : 0.5,
    }

    hybridParams = copy.copy(humanParams)
    hybridParams["name"] = "hybrid"
    hybridParams["count"] = 5
    hybridParams["function"] = SwitchVTypeFn("robot", 0.5, initCarFn=randomChangeLaneFn)

    opts = {
            "paramsList" : [humanParams, robotParams, hybridParams],
            "simSteps"   : 500,
            "tag"        : "aggressiveFasterLane"
            }

    sim = LoopSim("loopsim", length=1000, numLanes=2, simStepLength=0.5)
    sim.simulate(opts)
    sim.plot(show=True, save=True)
