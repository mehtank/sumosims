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
        traci.vehicle.moveTo(name, starte + "_" + repr(lane), startx)
        lane = (lane + 1) % numlanes

    #traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))
    for step in range(1000):
        traci.simulationStep()

        '''
        #res = traci.vehicle.getSubscriptionResults(vehID)
        myx = 0 #res[tc.VAR_LANEPOSITION] + edgestarts[res[tc.VAR_ROAD_ID]]

        alldiff = {}
        for (e, s) in edgestarts.items():
            allv = traci.edge.getLastStepVehicleIDs(e)
            for v in allv:
                if v != vehID:
                    alldiff[v] = (s + traci.vehicle.getLanePosition(v) - myx) % length
        mn = min(alldiff, key=alldiff.get)
        mx = max(alldiff, key=alldiff.get)

        if (step % 200) == 0:
            print "Step %d :: " % step, 
            print "  robot @ %6.2fm, " % myx,
            print mn, " ahead @ %6.2fm, " % alldiff[mn], 
            print mx, " behind @ %6.2fm." % (length-alldiff[mx])
        '''
    traci.close()
    sys.stdout.flush()

# this is the main entry point of this script
if __name__ == "__main__":
    from makecirc import makecirc, makenet
    from parsexml import parsexml
    from plots import pcolor, pcolor_multi

    base="circsweep"
    length=1000
    maxspeed=30
    numlanes=2
    numcars=100

    l4 = length/4.
    edgestarts = {"bottom": 0, "right": l4, "top": 2*l4, "left": 3*l4}

    cfgfn, nsfn, atfn, lcfn = config(base, length, numlanes, maxspeed)
    emsfn = "data/%s.emission.xml"%base

    sumoBinary = checkBinary('sumo')
    sumoProcess = subprocess.Popen([
            sumoBinary, 
            "--no-step-log",
            "-c", cfgfn,
            "--emission-output", emsfn, 
            "--remote-port", str(PORT)], 
        stdout=sys.stdout, stderr=sys.stderr)
    run(numcars, numlanes, edgestarts)
    sumoProcess.wait()


    print "Parsing xml file %s..." % nsfn
    alldata, trng, xrng, speeds, lanespeeds = parsexml(nsfn, edgestarts, length)

    print "Generating interpolated plot..."
    plt = pcolor_multi("Traffic jams (%d lanes, %d cars)" % (numlanes, numcars), 
            (xrng, "Position along loop (m)"),
            (trng, "Time (s)"),
            (lanespeeds, 0, maxspeed, "Speed (m/s)"))

    plt.show()
    print "Done!"
