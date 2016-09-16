import numpy as np
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
    x, y = np.meshgrid(xrng, yrng)
    cax = ax.pcolormesh(x, y, np.array(s),
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

def mybp(vax, bpdata, bppos, label, ltcolor, dkcolor):
    bp = vax.boxplot(bpdata, positions=bppos, widths=0.6, patch_artist=True)
    for box in bp['boxes']:
        box.set( facecolor = ltcolor )
    for line in bp['medians']:
            # get position data for median line
            x1, y = line.get_xydata()[0] # left of median line
            x2, y = line.get_xydata()[1] # right of median line
            # overlay median value
            vax.text((x1+x2)/2, y, '%.1f' % y, horizontalalignment='center') 
    vax.set_ylabel(label, color=dkcolor)
    for tl in vax.get_yticklabels():
        tl.set_color(dkcolor)

def pcolor_multi(title, (xrng, xlabel), 
                  (yrng, ylabel), 
                  (vdict, vlabel), 
                  (sdict, smin, smax, slabel),
                  (ldict, llabel),
                  (fdict, fmin, fmax, flabel)):

    numlanes = len(sdict)

    fig, axarr = plt.subplots(numlanes+2, 2, 
            figsize=(16, 16), dpi=100)

    axarr[-2,0].axis('off')
    axarr[-2,1].axis('off')
    vax = axarr[-1,0]
    fax = axarr[-1,1]

    x, y = np.meshgrid(xrng, yrng)

    for (ax2, ax, sid) in zip(axarr[:,0], axarr[:,1], sorted(sdict)):
        tv = T(np.array(sdict[sid]))
        cax = ax.pcolormesh(T(y), T(x), tv,
                vmin=smin, vmax=smax, 
                cmap=my_cmap)
        ax.set_ylabel(xlabel + "\nLane %s"%sid)
        ax.axis('tight')

        vmn = np.min(tv, axis=0)
        v25 = np.percentile(tv, 25, axis=0)
        v75 = np.percentile(tv, 75, axis=0)
        vmx = np.max(tv, axis=0)

        fax.plot(yrng, fdict[sid], label="lane %s" % sid)

        handles, labels = fax.get_legend_handles_labels()
        lbl = handles[-1]
        linecolor = lbl.get_c()
        linecolor = 'b'
        #fig.text(0.5, 0.95, 'Lane %s'%s, transform=fig.transFigure, horizontalalignment='center')
        #ax.set_title("lane %s" % sid, color=linecolor, x=-0.1)

        lc = colors.colorConverter.to_rgba(linecolor, alpha=0.1)
        ax2.fill_between(yrng, vmn, vmx, color=lc)
        lc = colors.colorConverter.to_rgba(linecolor, alpha=0.25)
        ax2.fill_between(yrng, v25, v75, color=lc)
        ax2.plot(yrng, vdict[sid], label="lane %s" % sid, color=linecolor)

        ax2.set_ylabel(vlabel + "\nLane %s"%sid)
        ax2.set_ylim([smin, smax])

    ax.set_xlabel(ylabel)
    ax2.set_xlabel(ylabel)

    boxplotdata1 = [[]]
    boxplotdata2 = [[]]
    boxplotpos1 = [1]
    boxplotpos2 = [2]
    boxplotlabels = ["All lanes"]
    bp = 4
    for lid in sorted(ldict):
        #boxplotdata.append(lt)
        lt = ldict[lid]
        ft = fdict[lid]
        boxplotdata1[0].extend(lt[len(lt)/2:])
        boxplotdata2[0].extend(ft[len(ft)/2:])
        boxplotdata1.append(lt[len(lt)/2:])
        boxplotdata2.append(ft[len(ft)/2:])
        boxplotlabels.append("lane %s" % lid)
        boxplotpos1.append(bp)
        boxplotpos2.append(bp+1)
        bp+=3
        # print "Total looptime, lane %s:" % lid, np.mean(lt[100:]), np.percentile(lt[100:], (0, 25, 75, 100))
        # print "Total fuel consumed, lane %s:" % lid, np.mean(ft[100:]), np.percentile(ft[100:], (0, 25, 75, 100))

    vax2 = vax.twinx()
    mybp(vax, boxplotdata1, boxplotpos1, llabel, '#9999ff', 'b')
    mybp(vax2, boxplotdata2, boxplotpos2, flabel, '#ff9999', 'r')

    vax.set_xticklabels([""] + boxplotlabels)
    vax.set_xticks([0] + [x*3+1.5 for x in range(len(boxplotlabels))])
    vax2.set_xticks([0] + [x*3+1.5 for x in range(len(boxplotlabels))])
    vax.set_title(title)

    fax.set_ylabel(flabel)
    if fmin is not None and fmax is not None:
        fax.set_ylim([fmin, fmax])
    fax.set_xlabel(ylabel)
    '''
    fig.text(0.5, 0.975, title, 
            horizontalalignment='center', verticalalignment='top')
    '''
    # Add colorbar
    fig.subplots_adjust(right=0.85)
    if numlanes == 2:
        cbm = 0.52
        cbl = 0.38
    elif numlanes == 1:
        cbm=0.665
        cbl=0.235
    else:
        cbm=0.1
        cbl=0.8

    cbar_ax = fig.add_axes([0.89, cbm, 0.02, cbl])

    ticks = np.linspace(smin, smax, 6)
    cbar = fig.colorbar(cax, cax=cbar_ax, ticks=ticks)
    cbar.ax.set_yticklabels(ticks)  # vertically oriented colorbar
    cbar.ax.set_ylabel(slabel, rotation=270, labelpad=20)

    return plt
