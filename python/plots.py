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
                  (sdict, smin, smax, slabel)):

    numlanes = len(sdict)

    fig, axarr = plt.subplots(numlanes+1, sharex=True, figsize=(6, 8), dpi=128)

    x, y = meshgrid(xrng, yrng)

    for (ax, sid) in zip(axarr, sorted(sdict)):
        tv = T(array(sdict[sid]))
        cax = ax.pcolormesh(T(y), T(x), tv,
                vmin=smin, vmax=smax, 
                cmap=my_cmap)
        ax.set_title("lane %s" % sid)
        ax.set_ylabel(xlabel)
        ax.axis('tight')

        dx = T(diff(x))
        # throws out last velocity
        dt = dx * 1./tv[:-1,:]
        ts = sum(diff(xrng))/sum(dt, axis=0)
        axarr[-1].plot(yrng, ts, label="lane %s" % sid)

    axarr[-1].set_ylabel("Average loop speed (m/s)")
    axarr[-1].legend(bbox_to_anchor=(0., 1.02, 1., .051), loc=3,
                       ncol=numlanes, mode="expand", borderaxespad=0.)
    axarr[-1].set_xlabel(ylabel)
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
