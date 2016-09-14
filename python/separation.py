import subprocess, sys
import random

# Make sure $SUMO_HOME/tools is in $PYTHONPATH
from sumolib import checkBinary
import traci
import traci.constants as tc

import config as c


vehID = "robot"

def run():
    """execute the TraCI control loop"""
    traci.init(c.PORT)
    traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))
    for step in range(40):
        traci.simulationStep()

        res = traci.vehicle.getSubscriptionResults(vehID)
        myx = res[tc.VAR_LANEPOSITION] + c.EDGESTARTS[res[tc.VAR_ROAD_ID]]

        alldiff = {}
        for (e, s) in c.EDGESTARTS.items():
            allv = traci.edge.getLastStepVehicleIDs(e)
            for v in allv:
                if v != vehID:
                    alldiff[v] = (s + traci.vehicle.getLanePosition(v) - myx) % c.LENGTH
        mn = min(alldiff, key=alldiff.get)
        mx = max(alldiff, key=alldiff.get)

        if (step % 1) == 0:
            print "Step %d :: " % step, 
            print "  robot @ %6.2fm, " % myx,
            print mn, " ahead @ %6.2fm, " % alldiff[mn], 
            print mx, " behind @ %6.2fm." % (c.LENGTH-alldiff[mx])
    traci.close()
    sys.stdout.flush()


# this is the main entry point of this script
if __name__ == "__main__":
    sumoBinary = checkBinary('sumo')
    sumoProcess = subprocess.Popen([
            sumoBinary, 
            "--no-step-log",
            "-c", "circular.sumo.cfg", 
            "--remote-port", str(c.PORT)],
        stdout=sys.stdout, stderr=sys.stderr)
    run()
    sumoProcess.wait()
