import subprocess
import sys
import os
import errno

# Make sure $SUMO_HOME/tools is in $PYTHONPATH
from sumolib import checkBinary
import traci
import traci.constants as tc

import config as defaults
from makecirc import makecirc, makenet
from parsexml import parsexml
from plots import pcolor, pcolor_multi


KNOWN_PARAMS = {
        "maxSpeed"      : traci.vehicle.setMaxSpeed,
        "accel"         : traci.vehicle.setAccel,
        "decel"         : traci.vehicle.setAccel,
        "sigma"         : traci.vehicle.setImperfection,
        "tau"           : traci.vehicle.setTau,
        "speedFactor"   : traci.vehicle.setSpeedFactor,
        "speedDev"      : traci.vehicle.setSpeedDeviation,
        }

def ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    return path

class LoopSim:

    def __init__(self, name, length, numLanes, 
            maxSpeed=defaults.SPEED_LIMIT, port=defaults.PORT):
        self.name = "%s-%dm%dl" % (name, length, numLanes)
        self.length = length
        self.numLanes = numLanes

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
                maxSpeed=maxSpeed,
                path=self.net_path)
        self.port = port

    def _mkdirs(self, name):
        self.net_path = ensure_dir("%s" % defaults.NET_PATH)
        self.data_path = ensure_dir("%s" % defaults.DATA_PATH)
        self.img_path = ensure_dir("%s" % defaults.IMG_PATH)

    def _simInit(self, suffix):
        self.cfgfn, self.outs = makecirc(self.name+suffix, 
                netfn=self.netfn, 
                numcars=0, 
                dataprefix = defaults.DATA_PATH)

        # Start simulator
        sumoBinary = checkBinary('sumo')
        self.sumoProcess = subprocess.Popen([
                sumoBinary, 
                "--no-step-log",
                "-c", self.cfgfn,
                "--remote-port", str(self.port)], 
            stdout=sys.stdout, stderr=sys.stderr)

        # Initialize TraCI
        traci.init(self.port)

        self.humanCars = []
        self.robotCars = []

    def _getEdge(self, x):
        for (e, s) in self.edgestarts.iteritems():
            if x >= s:
                starte = e
                startx = x-s
        return starte, startx

    def _getX(self, edge, position):
        return position + self.edgestarts[edge]

    def _createCar(self, name, x, lane, carParams):
        starte, startx = self._getEdge(x)

        laneSpread = carParams.pop("laneSpread", True)
        if laneSpread is not True:
            lane = laneSpread

        traci.vehicle.addFull(name, "route"+starte)
        traci.vehicle.moveTo(name, starte + "_" + repr(lane), startx)

        if carParams is not None:
            for (pname, pvalue) in carParams.iteritems():
                if pname in KNOWN_PARAMS:
                    KNOWN_PARAMS[pname](name, pvalue)
                else:
                    traci.vehicle.setParameter(name, pname, repr(pvalue))

    def _addCars(self, humanParams, robotParams):
        numHumanCars = humanParams.pop("count", 0)
        numRobotCars = robotParams.pop("count", 0)
        numCars = numHumanCars + numRobotCars

        # Add numCars cars to simulation
        lane = 0

        humansLeft = numHumanCars
        robotsLeft = numRobotCars

        for i in range(numCars):
            x = self.length * i / numCars
            # evenly distribute robot cars and human cars
            if (robotsLeft == 0 or 
                (humansLeft > 0 and 
                 ((humansLeft-1.0)/robotsLeft >= 1.0*numHumanCars/numRobotCars))):
                    # add human car
                    name = "human%03d" % i
                    self.humanCars.append(name)
                    self._createCar(name, x, lane, humanParams.copy())
                    humansLeft -= 1
            else:
                    # add robot car
                    name = "robot%03d" % i
                    self.robotCars.append(name)
                    self._createCar(name, x, lane, robotParams.copy())
                    robotsLeft -= 1

            lane = (lane + 1) % self.numLanes

    def _run(self, simSteps, humanCarFn, robotCarFn):
        for step in range(simSteps):
            traci.simulationStep()
            self.allCars = []
            for v in self.humanCars + self.robotCars:
                car = {}
                car["id"] = v
                car["edge"] = traci.vehicle.getRoadID(v)
                position = traci.vehicle.getLanePosition(v)
                car["lane"] = traci.vehicle.getLaneIndex(v)
                car["x"] = self._getX(car["edge"], position)
                car["v"] = traci.vehicle.getSpeed(v)
                self.allCars.append(car)
            self.allCars.sort(key=lambda x: x["x"])

            for (idx, car) in enumerate(self.allCars):
                if humanCarFn is not None and car["id"] in self.humanCars:
                    humanCarFn((idx, car), self, step)
                elif robotCarFn is not None and car["id"] in self.robotCars:
                    robotCarFn((idx, car), self, step)

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


    def simulate(self, opts):

        self.label = opts.get("label", None)
        tag = opts.get("tag", None)

        humanParams = opts.get("humanParams", dict())
        humanCarFn = humanParams.pop("function", None)
        self.numHumans = humanParams.get("count", 100)
        humanMaxSpeed = humanParams.get("maxSpeed", 30)

        robotParams = opts.get("robotParams", dict())
        robotCarFn = robotParams.pop("function", None)
        self.numRobots = robotParams.get("count", 0)
        robotMaxSpeed = robotParams.get("maxSpeed", 30)

        self.numCars = self.numHumans+self.numRobots

        simSteps = opts.get("simSteps", 500)

        self.maxSpeed = max(humanMaxSpeed, robotMaxSpeed)

        if self.label is None:
            self.label = "h%03d-r%03d" % (self.numHumans, self.numRobots)
        if tag is not None:
            self.label += "-" + tag

        self._simInit("-" + self.label)
        self._addCars(humanParams, robotParams)
        self._run(simSteps, humanCarFn, robotCarFn)

    def plot(self, show=True, save=False):
        # Plot results
        nsfn = self.outs["netstate"]
        alldata, trng, xrng, speeds, lanespeeds = parsexml(nsfn, self.edgestarts, self.length)

        print "Generating interpolated plot..."
        plt = pcolor_multi("Traffic jams (%d lanes, %d humans, %d robots)" % 
                    (self.numLanes, self.numHumans, self.numRobots), 
                (xrng, "Position along loop (m)"),
                (trng, "Time (s)"),
                (lanespeeds, 0, self.maxSpeed, "Speed (m/s)"))

        fig = plt.gcf()
        if show:
            plt.show()
        if save:
            fig.savefig(defaults.IMG_PATH + self.name + "-" + self.label + ".png")
        return plt

# this is the main entry point of this script
if __name__ == "__main__":
    from carfns import randomChangeLaneFn, ACCFnBuilder, changeFasterLaneBuilder

    humanParams = {
            "count"       :  40,
            "maxSpeed"    :  40,
            "accel"       :   4,
            "decel"       :   6,
            #"function"    : changeFasterLaneBuilder(),
            "laneSpread"  : 0,
            "lcSpeedGain" : 100,
            }

    robotParams = {
            "count"       :   0,
            "maxSpeed"    :  40,
            "accel"       :   4,
            "decel"       :   6,
            #"function"    : ACCFnBuilder(follow_sec = 3.0, max_speed = 26.8, gain = 0.1),
            "laneSpread"  : 0,
            }

    opts = {
            "humanParams": humanParams,
            "robotParams": robotParams,
            "simSteps"   : 500,
            "tag"        : "laneChange"
            }

    sim = LoopSim("loopsim", length=1000, numLanes=2)
    sim.simulate(opts)
    sim.plot(show=True, save=True)
