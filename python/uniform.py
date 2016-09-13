import subprocess, sys
import random

# Make sure $SUMO_HOME/tools is in $PYTHONPATH
from sumolib import checkBinary
import traci
import traci.constants as tc

# the port used for communicating with your sumo instance
PORT = 8873


vehID = "robot"

def config(base, length, numlanes, maxspeed):
    netfn = makenet(base, length=length, lanes=numlanes)
    name = "%s-%dl-%02d" % (base, numlanes, numcars)
    # set up simulation
    return makecirc(name, netfn=netfn, numcars=0, maxspeed=maxspeed)

def run(numcars, numlanes, edgestarts):
    """execute the TraCI control loop"""
    traci.init(PORT)
    lane = 0
    for i in range(numcars):
        name = "car%03d" % i
        x = length * i / numcars
        for (e, s) in edgestarts.iteritems():
            if x >= s:
                starte = e
                startx = x-s

        traci.vehicle.addFull(name, "route"+starte)
        traci.vehicle.setAccel(name, 10)
        traci.vehicle.moveTo(name, starte + "_" + repr(lane), startx)
        #traci.vehicle.setParameter(name, "lcSpeedGain", "1000000")
        #lane = (lane + 1) % numlanes

    for step in range(500):
        traci.simulationStep()
    traci.close()
    sys.stdout.flush()

# this is the main entry point of this script
if __name__ == "__main__":
    from makecirc import makecirc, makenet
    from parsexml import parsexml
    from plots import pcolor, pcolor_multi

    base="circsweep"
    length=1000
    numlanes=2
    maxspeed=30

    numcars=60

    l4 = length/4.
    edgestarts = {"bottom": 0, "right": l4, "top": 2*l4, "left": 3*l4}

    cfgfn, outs = config(base, length, numlanes, maxspeed)

    sumoBinary = checkBinary('sumo')
    sumoProcess = subprocess.Popen([
            sumoBinary, 
            "--no-step-log",
            "-c", cfgfn,
            "--remote-port", str(PORT)], 
        stdout=sys.stdout, stderr=sys.stderr)
    run(numcars, numlanes, edgestarts)
    sumoProcess.wait()

    nsfn = outs["netstate"]
    print "Parsing xml file %s..." % nsfn
    alldata, trng, xrng, speeds, lanespeeds = parsexml(nsfn, edgestarts, length)

    print "Generating interpolated plot..."
    plt = pcolor_multi("Traffic jams (%d lanes, %d cars)" % (numlanes, numcars), 
            (xrng, "Position along loop (m)"),
            (trng, "Time (s)"),
            (lanespeeds, 0, maxspeed, "Speed (m/s)"))

    #plt.show()
    plt.savefig("img/2lane.png")
    print "Done!"
