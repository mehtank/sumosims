import subprocess
import sys

from parsexml import parsexml
from plots import pcolor


roufn = "circular.rou.xml"
cfgfn = "circular.sumo.cfg"

for numcars in (5, 10, 15, 20, 25, 30):
    with open(roufn, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>')
        f.write('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">')
        f.write('    <vType accel="1.5" decel="4.5" id="car" length="5" maxSpeed="30"/>')
        f.write('    <flow begin="0" departPos="free" id="carRight" period="1" number="%d" route="routeRight" type="car"/>' % numcars)
        f.write('    <flow begin="0" departPos="free" id="carTop" period="1" number="%d" route="routeTop" type="car"/>' % numcars)
        f.write('    <flow begin="0" departPos="free" id="carLeft" period="1" number="%d" route="routeLeft" type="car"/>' % numcars)
        f.write('    <flow begin="0" departPos="free" id="carBottom" period="1" number="%d" route="routeBottom" type="car"/>' % numcars)
        f.write('</routes>')

    with open(cfgfn, 'w') as f:
	f.write('<?xml version="1.0" encoding="UTF-8"?>')
	f.write('<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">')
	f.write('    <input>')
	f.write('        <net-file value="circular.net.xml"/>')
	f.write('        <route-files value="circular.rou.xml"/>')
	f.write('        <additional-files value="circular.add.xml"/>')
	f.write('    </input>')
	f.write('    <output>')
	f.write('        <netstate-dump value="data/circulardump%02d.xml"/>' % numcars)
	f.write('    </output>')
	f.write('    <time>')
	f.write('        <begin value="0"/>')
	f.write('        <end value="3000"/>')
	f.write('    </time>')
	f.write('</configuration>')

    # run simulation
    retcode = subprocess.call(
	['sumo', "-c", cfgfn, "--no-step-log"], stdout=sys.stdout, stderr=sys.stderr)
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
