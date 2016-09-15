from numpy import meshgrid, array, linspace, diff, sum
from numpy import transpose as T
import matplotlib.pyplot as plt
import matplotlib.colors as colors


cdict = {
        'red'  :  ((0., 0., 0.), (0.2, 1., 1.), (0.6, 1., 1.), (1., 0., 0.)),
        'green':  ((0., 0., 0.), (0.2, 0., 0.), (0.6, 1., 1.), (1., 1., 1.)),
        'blue' :  ((0., 0., 0.), (0.2, 0., 0.), (0.6, 0., 0.), (1., 0., 0.))
        }
my_cmap = colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

def scatter(title, (x, xlabel), 
                   (y, ylabel), 
                   (s, smin, smax, slabel)):

    fig, ax = plt.subplots()

    cax = ax.scatter(x, y, c=s, 
            vmin=smin, vmax=smax, 
            s=3, edgecolors='none', 
            cmap=my_cmap)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.margins(0)
    ax.invert_yaxis()

    # Add colorbar
    ticks = [smin, (smin+smax)/2, smax]
    cbar = fig.colorbar(cax, ticks=ticks)
    cbar.ax.set_yticklabels(ticks)  # vertically oriented colorbar
    cbar.ax.set_ylabel(slabel, rotation=270, labelpad=20)

    return plt

def pcolor(title, (xrng, xlabel), 
                  (yrng, ylabel), 
                  (s, smin, smax, slabel)):

    fig, ax = plt.subplots()

    #y, x = mgrid[yrng, xrng]
    #cax = ax.pcolor(x, y, s, 
    x, y = meshgrid(xrng, yrng)
    cax = ax.pcolormesh(x, y, array(s),
            vmin=smin, vmax=smax, 
            cmap=my_cmap)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.axis('tight')
    ax.invert_yaxis()

    # Add colorbar
    ticks = [smin, (smin+smax)/2, smax]
    cbar = fig.colorbar(cax, ticks=ticks)
    cbar.ax.set_yticklabels(ticks)  # vertically oriented colorbar
    cbar.ax.set_ylabel(slabel, rotation=270, labelpad=20)

    return plt

def pcolor_multi(title, (xrng, xlabel), 
                  (yrng, ylabel), 
                  (vdict, vlabel), 
                  (sdict, smin, smax, slabel),
                  (odict, olabel)):

    numlanes = len(sdict)

    fig, axarr = plt.subplots(numlanes+1, 2, 
            sharex=True, 
            figsize=(8, 6), dpi=128)

    x, y = meshgrid(xrng, yrng)

    for (ax, ax2, sid) in zip(axarr[:,0], axarr[:,1], sorted(sdict)):
        tv = T(array(sdict[sid]))
        cax = ax.pcolormesh(T(y), T(x), tv,
                vmin=smin, vmax=smax, 
                cmap=my_cmap)
        ax.set_ylabel(xlabel)
        ax.axis('tight')

        tv = T(array(odict[sid]))
        cax = ax2.pcolormesh(T(y), T(x), tv)
        ax2.axis('tight')

        axarr[-1,0].plot(yrng, vdict[sid], label="lane %s" % sid)
        handles, labels = axarr[-1,0].get_legend_handles_labels()
        lbl = handles[-1]
        ax.set_title("lane %s" % sid, color=lbl.get_c())

    axarr[-1,0].set_ylabel(vlabel)
    axarr[-1,0].set_xlabel(ylabel)
    fig.text(0.5, 0.975, title, 
            horizontalalignment='center', verticalalignment='top')
    # Add colorbar
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.84, 0.1, 0.02, 0.8])

    ticks = linspace(smin, smax, 6)
    cbar = fig.colorbar(cax, cax=cbar_ax, ticks=ticks)
    cbar.ax.set_yticklabels(ticks)  # vertically oriented colorbar
    cbar.ax.set_ylabel(slabel, rotation=270, labelpad=20)

    return plt
