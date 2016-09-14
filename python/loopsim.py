import subprocess
import sys
import os
import errno

# Make sure $SUMO_HOME/tools is in $PYTHONPATH
from sumolib import checkBinary
import traci
import traci.constants as tc

import config as c
from makecirc import makecirc, makenet
from parsexml import parsexml
from plots import pcolor, pcolor_multi
from util import headway


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

    def _addCars(self, numCars, maxSpeed, accel, carParams, laneSpread, isRobot):
        # Add numCars cars to simulation
        lane = 0
        for i in range(numCars):
            if isRobot:
                name = "robot%03d" % i
                self.robotCars.append(name)
            else:
                name = "human%03d" % i
                self.humanCars.append(name)

            starte, startx = self._getEdge(self.length * i / numCars)

            traci.vehicle.addFull(name, "route"+starte)
            traci.vehicle.moveTo(name, starte + "_" + repr(lane), startx)
            traci.vehicle.setMaxSpeed(name, maxSpeed)
            if accel is not None:
                traci.vehicle.setAccel(name, accel)
            if carParams is not None:
                for (pname, pvalue) in carParams.iteritems():
                    traci.vehicle.setParameter(name, pname, repr(pvalue))

            if laneSpread:
                lane = (lane + 1) % self.numLanes

    def _run(self, simSteps, humanCarFn, robotCarFn):
        for step in range(simSteps):
            traci.simulationStep()
            if humanCarFn is not None:
                for v in self.humanCars:
                    humanCarFn(v, robotCars=self.robotCars, humanCars=self.humanCars)
            if robotCarFn is not None:
                for v in self.robotCars:
                    robotCarFn(v, robotCars=self.robotCars, humanCars=self.humanCars)

        traci.close()
        sys.stdout.flush()
        self.sumoProcess.wait()

    def simulate(self, opts):

        self.label = opts.get("label", None)
        tag = opts.get("tag", None)

        humanParams = opts.get("humanParams", dict())
        self.numHumans = humanParams.pop("count", 100)
        humanMaxSpeed = humanParams.pop("maxSpeed", 30)
        humanAccel = humanParams.pop("accel", None)
        humanCarFn = humanParams.pop("function", None)
        humanSpread = humanParams.pop("laneSpread", False)

        robotParams = opts.get("robotParams", dict())
        self.numRobots = robotParams.pop("count", 0)
        robotMaxSpeed = robotParams.pop("maxSpeed", 30)
        robotAccel = robotParams.pop("accel", None)
        robotCarFn = robotParams.pop("function", None)
        robotSpread = robotParams.pop("laneSpread", False)

        simSteps = opts.get("simSteps", 500)

        self.maxSpeed = max(humanMaxSpeed, robotMaxSpeed)

        if self.label is None:
            self.label = "h%03d-r%03d" % (self.numHumans, self.numRobots)
        if tag is not None:
            self.label += "-" + tag

        self._simInit("-" + self.label)
        self._addCars(self.numHumans, humanMaxSpeed, humanAccel, humanParams, humanSpread, isRobot=False)
        self._addCars(self.numRobots, robotMaxSpeed, robotAccel, robotParams, robotSpread, isRobot=True)
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

    def randomChangeLaneFn(v, humanCars=None, robotCars=None):
        li = traci.vehicle.getLaneIndex(v)
        if random.random() > .99:
            traci.vehicle.changeLane(v, 1-li, 1000)


    def ACCFn(v, humanCars=None, robotCars=None):
        # traci.vehicle.setTau(v, 0)
        li = traci.vehicle.getLaneIndex(v)
        ((front_vID, front_dist), (back_vID, back_dist)) = headway(v, humanCars + robotCars, lane=li, length=c.LENGTH)
        print (front_vID, front_dist), (back_vID, back_dist)
        if random.random() > .99:
            traci.vehicle.changeLane(v, 1-li, 1000)

    humanParams = {
            "count"       :  80,
            "maxSpeed"    :  30,
            "accel"       :   2,
            "function"    : ACCFn,
            "laneSpread"  : False,
            "lcSpeedGain" : 100,
            }

    opts = {
            "humanParams": humanParams,
            "simSteps"   :    500,
            "tag"      : ".01-lane-change"
            }

    sim = LoopSim("loopsim", length=1000, numLanes=2)
    sim.simulate(opts)
    sim.plot(show=True, save=True)
