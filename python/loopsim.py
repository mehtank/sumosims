import subprocess
import sys
import os
import errno

# Make sure $SUMO_HOME/tools is in $PYTHONPATH
from sumolib import checkBinary
import traci
import traci.constants as tc

from makecirc import makecirc, makenet
from parsexml import parsexml
from plots import pcolor, pcolor_multi


# the port used for communicating with your sumo instance
PORT = 8873

NET_PATH = "net/"
IMG_PATH = "img/"
DATA_PATH = "data/"

def ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    return path

class LoopSim:

    def __init__(self, name, length, numLanes, port=PORT):
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
                path=self.net_path)
        self.port = port

    def _mkdirs(self, name):
        self.net_path = ensure_dir("%s" % NET_PATH)
        self.data_path = ensure_dir("%s" % DATA_PATH)
        self.img_path = ensure_dir("%s" % IMG_PATH)

    def _simInit(self, suffix):
        self.cfgfn, self.outs = makecirc(self.name+suffix, 
                netfn=self.netfn, 
                numcars=0, 
                dataprefix = DATA_PATH)

        # Start simulator
        sumoBinary = checkBinary('sumo')
        self.sumoProcess = subprocess.Popen([
                sumoBinary, 
                "--no-step-log",
                "-c", self.cfgfn,
                "--remote-port", str(PORT)], 
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
        maxSpeed = carParams.pop("maxSpeed", 30)
        accel = carParams.pop("accel", None)
        laneSpread = carParams.pop("laneSpread", True)
        if laneSpread is not True:
            lane = laneSpread

        traci.vehicle.addFull(name, "route"+starte)
        traci.vehicle.moveTo(name, starte + "_" + repr(lane), startx)
        traci.vehicle.setMaxSpeed(name, maxSpeed)
        if accel is not None:
            traci.vehicle.setAccel(name, accel)
        if carParams is not None:
            for (pname, pvalue) in carParams.iteritems():
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
            allCars = {}
            for v in self.humanCars + self.robotCars:
                car = {}
                car["edge"] = traci.vehicle.getRoadID(v)
                car["position"] = traci.vehicle.getLanePosition(v)
                car["lane"] = traci.vehicle.getLaneIndex(v)
                car["x"] = self._getX(edge, position)
                car["v"] = traci.vehicle.getSpeed(v)
                allCars[v] = car

            if humanCarFn is not None:
                for v in self.humanCars:
                    humanCarFn(v)
            if robotCarFn is not None:
                for v in self.robotCars:
                    robotCarFn(v)

        traci.close()
        sys.stdout.flush()
        self.sumoProcess.wait()

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
            fig.savefig(IMG_PATH + self.name + "-" + self.label + ".png")
        return plt

# this is the main entry point of this script
if __name__ == "__main__":
    import random

    def humanCarFn(v):
        li = traci.vehicle.getLaneIndex(v)
        if random.random() > .99:
            traci.vehicle.changeLane(v, 1-li, 1000)

    humanParams = {
            "count"       :  80,
            "maxSpeed"    :  30,
            "accel"       :   2,
            "function"    : humanCarFn,
            "laneSpread"  : 0,
            "lcSpeedGain" : 100,
            }

    def robotCarFn(v):
        li = traci.vehicle.getLaneIndex(v)
        if random.random() > .99:
            traci.vehicle.changeLane(v, 1-li, 1000)

    robotParams = {
            "count"       :   7,
            "maxSpeed"    :  30,
            "accel"       :   2,
            "function"    : robotCarFn,
            "laneSpread"  : 0,
            }

    opts = {
            "humanParams": humanParams,
            "robotParams": robotParams,
            "simSteps"   : 500,
            "tag"        : ".01-lane-change"
            }

    sim = LoopSim("loopsim", length=1000, numLanes=2)
    sim.simulate(opts)
    sim.plot(show=True, save=True)
