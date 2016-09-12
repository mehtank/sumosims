from lxml import objectify
from scipy import interpolate

# TODO: command line argument?
fn = "data/circulardump.xml"

# TODO: Get values from .xml
edgestarts = {"bottom": 0, "right": 250, "top": 500, "left": 750}
maxpos = 1000
maxspeed = 30

# plot configuration
plotpoints = 100000
posstep = 10

print "Parsing xml file..."
obj = objectify.parse(file(fn)).getroot()

print "Extracting vehicle data..."
alldata = []
funcs = []
interps = []
xrng = range(0, maxpos, posstep)

for timestep in obj.timestep:
    t = float(timestep.get("time"))
    this = []
    for edge in timestep.edge:
        for lane in edge.lane:
            try:
                for vehicle in lane.vehicle:
                    name = vehicle.get("id")
                    v = float(vehicle.get("speed"))
                    x = float(vehicle.get("pos"))+edgestarts[edge.get("id")]
                    this.append({"name": name, "time": t, "position": x, "speed": v})
            except AttributeError:
                pass
    alldata.extend(this)
    interpx = [x["position"] for x in this]
    interpy = [x["speed"] for x in this]
    newx = []; newy = []
    newindex = interpx.index(max(interpx))
    newx.append(interpx[newindex] - maxpos)
    newy.append(interpy[newindex])
    newindex = interpx.index(min(interpx))
    newx.append(interpx[newindex] + maxpos)
    newy.append(interpy[newindex])
    interpx.extend(newx)
    interpy.extend(newy)

    f = interpolate.interp1d(interpx,
                             interpy,
                             assume_sorted=False)
    funcs.append((t, f))
    interps.append((t, f(xrng)))

# matplotlib scatterplot

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import random

# subsample data
#subdata = random.sample(alldata[8000:100000], 50000)
if len(alldata) > plotpoints:
    print "Randomly subsampling data from %d to %d..." % (len(alldata), plotpoints)
    subdata = random.sample(alldata, plotpoints)
else:
    subdata = alldata

x=[car["position"] for car in subdata]
y=[car["time"] for car in subdata]
s=[car["speed"] for car in subdata]

"""
x = [xp for xp in xrng for (t, f) in funcs]
y = [t for xp in xrng for (t, f) in funcs]
s = [f(xp) for xp in xrng for (t, f) in funcs]
"""
x = [xrng[i] for (t, vs) in interps for i in range(len(xrng))]
y = [t for (t, vs) in interps for i in range(len(xrng))]
s = [vs[i] for (t, vs) in interps for i in range(len(xrng))]

print "Generating plot..."
fig, ax = plt.subplots()

cdict = {
        'red'  :  ((0., 0., 0.), (0.2, 1., 1.), (0.6, 1., 1.), (1., 0., 0.)),
        'green':  ((0., 0., 0.), (0.2, 0., 0.), (0.6, 1., 1.), (1., 1., 1.)),
        'blue' :  ((0., 0., 0.), (0.2, 0., 0.), (0.6, 0., 0.), (1., 0., 0.))
        }
my_cmap = colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

ticks = [0, maxspeed/2, maxspeed]
cax = ax.scatter(x, y, c=s, 
        vmin=0, vmax=maxspeed, 
        s=3, edgecolors='none', 
        cmap=my_cmap)
ax.set_title('Traffic jams')
ax.set_ylabel('Time (s)')
ax.set_xlabel('Position along loop (m)')
ax.axis('tight')
ax.invert_yaxis()

# Add colorbar
cbar = fig.colorbar(cax, ticks=ticks)
cbar.ax.set_yticklabels(ticks)  # vertically oriented colorbar
cbar.ax.set_ylabel('Speed (m/s)', rotation=270, labelpad=20)

# TODO: command line argument?
plt.show()
#plt.savefig('labeled.png')

print "Done!"
