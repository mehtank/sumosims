import random

from parsexml import parsexml
from plots import scatter, pcolor


# TODO: command line argument?
fn = "data/circulardump.xml"

# TODO: Get values from .xml
edgestarts = {"bottom": 0, "right": 250, "top": 500, "left": 750}
maxpos = 1000
maxspeed = 30

# plot configuration
plotpoints = 100000

print "Parsing xml file..."
alldata, trng, xrng, speeds = parsexml(fn, edgestarts, maxpos)

'''
# matplotlib scatterplot

# subsample data
if len(alldata) > plotpoints:
    print "Randomly subsampling data from %d to %d..." % (len(alldata), plotpoints)
    subdata = random.sample(alldata, plotpoints)
else:
    subdata = alldata

x=[car["position"] for car in subdata]
y=[car["time"] for car in subdata]
s=[car["speed"] for car in subdata]

print "Generating scatter plot..."
plt = scatter("Traffic jams (subsampled data)", 
              (x, "Position along loop (m)"),
              (y, "Time (s)"),
              (s, 0, maxspeed, "Speed (m/s)"))

# TODO: command line argument?
#plt.show()
plt.savefig('data.png')
'''

print "Generating interpolated plot..."
plt = pcolor("Traffic jams (interpolated data)", 
             (xrng, "Position along loop (m)"),
             (trng, "Time (s)"),
             (speeds, 0, maxspeed, "Speed (m/s)"))

#plt.show()
plt.savefig('interp.png')
print "Done!"
