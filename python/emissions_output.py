import os
import sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib

if __name__ == "__main__":
    total_fuel = 0

    vehicles = sumolib.output.parse('circular.emission.xml', ['vehicle'])
    for veh in vehicles:
        total_fuel += float(veh.fuel)

    print "Total fuel consumed: %f" % total_fuel
