import subprocess
import sys

from makecirc import makecirc, makenet
from parsexml import parsexml
from plots import pcolor


base="circsweep"
length=1000
maxspeed=30

for numlanes in (1, 2, 3):
    netfn = makenet(base, length=length, lanes=numlanes)

    for numcars in (20, 40, 60, 80, 100, 120):
        name = "%s-%dl-%02d" % (base, numlanes, numcars)

        # set up simulation
        print "Setting up simulaton..."
        cfgfn, outs = makecirc(name, netfn=netfn, numcars=numcars, maxspeed=maxspeed)

        # run simulation
        print "Running simulaton..."
        retcode = subprocess.call(
            ['sumo', "-c", cfgfn, "--no-step-log"], 
            stdout=sys.stdout, stderr=sys.stderr)
        print(">> Simulation closed with status %s" % retcode)
        sys.stdout.flush()

        # TODO: Get values from .xml?
        l4 = length/4.
        edgestarts = {"bottom": 0, "right": l4, "top": 2*l4, "left": 3*l4}

        nsfn = outs["netstate"]
        print "Parsing xml file %s..." % nsfn
        trng, xrng, avgspeeds, lanespeeds, laneoccupancy = parsexml(nsfn, edgestarts, length)

        print "Generating interpolated plot..."
        plt = pcolor_multi("Traffic jams (%d lanes, %d cars)" % (numlanes, numcars), 
                    (xrng, "Position along loop (m)"),
                    (trng, "Time (s)"),
                    (lanespeeds, 0, maxspeed, "Speed (m/s)"))

        plt.savefig('img/interp-%s.png' % name)
        print "Done!"
