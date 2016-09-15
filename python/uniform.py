import subprocess, sys
import random

# Make sure $SUMO_HOME/tools is in $PYTHONPATH
from sumolib import checkBinary
import traci
import traci.constants as tc
from makecirc import makecirc, makenet

# the port used for communicating with your sumo instance
PORT = 8873


def config(base, length, numlanes, maxspeed):
    # Make loop network
    netfn = makenet(base, length=length, lanes=numlanes)
    # Define custom filenames based on numbers of lanes and cars
    name = "%s-%dl-%02d" % (base, numlanes, numcars)
    # Initialize simulation with no cars
    return makecirc(name, netfn=netfn, numcars=0, maxspeed=maxspeed)

def init(cfgfn):
    # Start simulator
    sumoBinary = checkBinary('sumo')
    sumoProcess = subprocess.Popen([
            sumoBinary, 
            "--no-step-log",
            "-c", cfgfn,
            "--remote-port", str(PORT)], 
        stdout=sys.stdout, stderr=sys.stderr)

    # Initialize TraCI
    traci.init(PORT)
    return sumoProcess

def addCar(i, lane):
    # Add i'th car of simulation to lane, uniformly around loop
    name = "car%03d" % i
    x = length * i / numcars
    for (e, s) in edgestarts.iteritems():
        if x >= s:
            starte = e
            startx = x-s

    traci.vehicle.addFull(name, "route"+starte)
    traci.vehicle.moveTo(name, starte + "_" + repr(lane), startx)
    traci.vehicle.setAccel(name, 10)
    #traci.vehicle.setParameter(name, "lcSpeedGain", "1000000")

def addCars(numcars, numlanes, edgestarts):
    # Add numcars cars to simulation
    lane = 0
    for i in range(numcars):
        addCar(i, lane)
        # commented: all in lane 0
        # uncommented: uniformly in all lanes
        #lane = (lane + 1) % numlanes

def run(sumoProcess, numSteps):
    for step in range(numSteps):
        traci.simulationStep()
    traci.close()
    sys.stdout.flush()
    sumoProcess.wait()

# this is the main entry point of this script
if __name__ == "__main__":
    from parsexml import parsexml
    from plots import pcolor, pcolor_multi

    base="circsweep"
    length=1000
    numlanes=2
    maxspeed=30

    numcars=60

    numSteps = 500

    # Still hacky but turns edgelengths into position along loop
    l4 = length/4.
    edgestarts = {"bottom": 0, "right": l4, "top": 2*l4, "left": 3*l4}

    # Do the thing
    print "Configuring simulation..."
    cfgfn, outs = config(base, length, numlanes, maxspeed)
    print "Initializing simulation..."
    spc = init(cfgfn)
    addCars(numcars, numlanes, edgestarts)
    print "Running simulation..."
    run(spc, numSteps)

    # Plot results
    nsfn = outs["netstate"]
    print "Parsing xml output file %s..." % nsfn
    trng, xrng, avgspeeds, lanespeeds, laneoccupancy = parsexml(nsfn, edgestarts, length)

    print "Generating interpolated plot..."
    plt = pcolor_multi("Traffic jams (%d lanes, %d cars)" % (numlanes, numcars), 
            (xrng, "Position along loop (m)"),
            (trng, "Time (s)"),
            (lanespeeds, 0, maxspeed, "Speed (m/s)"))

    #plt.show()
    plt.savefig("img/2lane.png")
    print "Done!"
