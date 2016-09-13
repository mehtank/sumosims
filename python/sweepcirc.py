import subprocess
import sys

from makecirc import makecirc
from parsexml import parsexml
from plots import pcolor


base="circsweep"

for numcars in (5, 10):
    name = "%s-%02d" % (base, numcars)

    # set up simulation
    print "Setting up simulaton..."
    makecirc(name, numcars=numcars)

    """
    # run simulation
    print "Running simulaton..."
    retcode = subprocess.call(
	['sumo', "-c", cfgfn, "--no-step-log"], 
        stdout=sys.stdout, stderr=sys.stderr)
    print(">> Simulation closed with status %s" % retcode)
    sys.stdout.flush()

    # TODO: Get values from .xml
    edgestarts = {"bottom": 0, "right": 250, "top": 500, "left": 750}
    maxpos = 1000
    maxspeed = 30

    fn = "data/circulardump%02d.xml" % numcars

    print "Parsing xml file %s..." % fn
    alldata, trng, xrng, speeds = parsexml(fn, edgestarts, maxpos)

    print "Generating interpolated plot..."
    plt = pcolor("Traffic jams (interpolated data, %d cars)" % numcars, 
                (xrng, "Position along loop (m)"),
                (trng, "Time (s)"),
                (speeds, 0, maxspeed, "Speed (m/s)"))

    plt.savefig('img/interp%02d.png' % numcars)
    print "Done!"
    """
