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

    def _getEdge(self, x):
        for (e, s) in self.edgestarts.iteritems():
            if x >= s:
                starte = e
                startx = x-s
        return starte, startx

    def _addCars(self, numCars, maxSpeed, accel, laneSpread, carParams):
        # Add numCars cars to simulation
        lane = 0
        for i in range(numCars):
            name = "car%03d" % i
            starte, startx = self._getEdge(self.length * i / numCars)

            traci.vehicle.addFull(name, "route"+starte)
            traci.vehicle.moveTo(name, starte + "_" + repr(lane), startx)
            traci.vehicle.setMaxSpeed(name, maxSpeed)
            if accel is not None:
                traci.vehicle.setAccel(name, accel)
            if carParams is not None:
                for (name, value) in carParams.iteritems():
                    traci.vehicle.setParameter(name, name, value)

            if laneSpread:
                lane = (lane + 1) % self.numLanes

    def _run(self, simSteps):
        for step in range(simSteps):
            traci.simulationStep()
        traci.close()
        sys.stdout.flush()
        self.sumoProcess.wait()

    def simulate(self, opts):

        self.label = opts.get("label", None)
        self.numCars = opts.get("numCars", 100)
        self.maxSpeed = opts.get("maxSpeed", 30)
        accel = opts.get("accel", None)
        laneSpread = opts.get("laneSpread", False)
        carParams = opts.get("carParams", None)
        simSteps = opts.get("simSteps", 500)

        if self.label is None:
            self.label = "n%03d-s%02d-a%02d" % (self.numCars, self.maxSpeed, accel)

        self._simInit("-" + self.label)
        self._addCars(self.numCars, self.maxSpeed, accel, laneSpread, carParams)
        self._run(simSteps)

    def plot(self, show=True, save=False):
        # Plot results
        nsfn = self.outs["netstate"]
        alldata, trng, xrng, speeds, lanespeeds = parsexml(nsfn, self.edgestarts, self.length)

        print "Generating interpolated plot..."
        plt = pcolor_multi("Traffic jams (%d lanes, %d cars)" % (self.numLanes, self.numCars), 
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
    params = {
            "lcSpeedGain" : "100",
            }

    opts = {
            "numCars"   :     60,
            "maxSpeed"  :     30,
            "accel"     :     10,
            "laneSpread":  False,
            "carParams" : None,
            "simSteps"  :    500,
            }

    sim = LoopSim("loopsim", length=1000, numLanes=2)
    sim.simulate(opts)
    sim.plot(show=True, save=True)
