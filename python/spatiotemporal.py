from lxml import objectify

# TODO: command line argument?
fn = "data/circulardump.xml"

print "Parsing xml file..."
obj = objectify.parse(file(fn)).getroot()

# TODO: Get values from .xml
edgestarts = {"bottom": 0, "right": 250, "top": 500, "left": 750}

print "Extracting vehicle data..."
alldata = []
for timestep in obj.timestep:
    t = float(timestep.get("time"))
    for edge in timestep.edge:
        for lane in edge.lane:
            try:
                for vehicle in lane.vehicle:
                    v = float(vehicle.get("speed"))
                    x = float(vehicle.get("pos"))+edgestarts[edge.get("id")]
                    alldata.append({"time": t, "position": x, "speed": v})
            except AttributeError:
                pass

"""
# XXX bokeh high-level scatterplot

from bokeh.charts import Scatter, output_file, show, figure
from bokeh.plotting import ColumnDataSource

data=dict(
    t=[car["time"] for car in alldata],
    x=[car["position"] for car in alldata],
    v=[car["speed"] for car in alldata],
)

p = Scatter(data, x='x', y='t', color='v', title="Spatiotemporal diagram (shaded by speed)", xlabel="Position along loop (m)", ylabel="Time (s)")

output_file("scatter.html")

show(p)


"""

"""
# XXX bokeh low-level scatterplot

from bokeh.plotting import figure, show, output_file

x=[car["position"] for car in alldata]
y=[car["time"] for car in alldata]
colors = ["#%02x%02x%02x" % (25*(10-car["speed"]), 25*car["speed"], 0) for car in alldata]

TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave,box_select,poly_select,lasso_select"

output_file("color_scatter.html", title="color_scatter.py example")

p = figure(tools=TOOLS)
p.scatter(x, y, fill_color=colors, fill_alpha=0.6, line_color=None)

show(p)  # open a browser
"""

# matplotlib scatterplot

import numpy as np
import matplotlib.pyplot as plt
import random

# subsample data
print "Randomly subsampling data..."
subdata = random.sample(alldata[8000:100000], 50000)
x=[car["position"] for car in subdata]
y=[car["time"] for car in subdata]
s=[car["speed"] for car in subdata]

# colorbar label
mn, mx = min(s), max(s)
mn = int(mn+1)
mx = int(mx)
md = int((mn+mx)/2)
ticks = [mn, md, mx]


print "Generating plot..."
fig, ax = plt.subplots()

cax = ax.scatter(x, y, c=s, s=3, edgecolors='none')
ax.set_title('Traffic jams')
ax.set_ylabel('Time (s)')
ax.set_xlabel('Position along loop (m)')
# TODO: set limits from data 
ax.set_xlim([0,1000])

# Add colorbar
cbar = fig.colorbar(cax, ticks=ticks)
cbar.ax.set_yticklabels(ticks)  # vertically oriented colorbar
cbar.ax.set_ylabel('Speed (m/s)', rotation=270)

# TODO: command line argument?
#plt.show()
plt.savefig('labeled.png')

print "Done!"
