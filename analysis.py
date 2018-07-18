"""Analysis.

Some plotting and other analysis functions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import subprocess as sp


def depickleLogFile(filename):
    """Read in the pickle'd full-log file from a run."""
    df = pickle.load(open('{}_step-log.pickle'.format(filename), 'rb'))
    # Note that we can find the min Chi2 val with:
    # m = df.set_index('Reduced Chi2').loc[min(df['Reduced Chi2'])]
    # This indexes the whole df by RedX2 and then finds the values that
    # minimize that new index.
    # Note, too, that it can be indexed either by slicing or by keys.
    df_a, df_b = df.loc['A', :], df.loc['B', :]
    min_X2_a = min(df_a['Reduced Chi2'])
    min_X2_b = min(df_b['Reduced Chi2'])
    # These come out as length-1 dicts
    best_fit_a = df_a.loc[df_a['Reduced Chi2'] == min_X2_a]
    best_fit_b = df_b.loc[df_b['Reduced Chi2'] == min_X2_b]

    out = {'full_log': df,
           'Disk A log': df_a,
           'Disk B log': df_b,
           'Best Fit A': best_fit_a,
           'Best Fit B': best_fit_b
           }
    return out


def parse_gridSearch_log(fname):
    """blah."""
    f_raw = open(fname).read().split('\n')
    f = filter(None, f_raw)

    chi_raws = f[1]
    diskA_ranges, diskB_ranges = f[4:10], f[12:18]

    diskA_bfvals, diskB_bfvals = f[19], f[21]

    diskA_bfvals = filter(None, diskA_bfvals.split(' '))[1:-1]
    diskB_bfvals = filter(None, diskB_bfvals.split(' '))[1:-1]

    diskA_bfvals = [float(el) for el in diskA_bfvals]
    diskB_bfvals = [float(el) for el in diskB_bfvals]


    r0 = filter(None, diskA_ranges[0].split(']')[0].split(' '))[1:]
    """Plot it
    f, axarr = plt.subplots(2, 2)
    axarr[0, 0].plot(x, y)
    axarr[0, 0].set_title('Axis [0,0]')
    axarr[0, 1].scatter(x, y)
    axarr[0, 1].set_title('Axis [0,1]')
    axarr[1, 0].plot(x, y ** 2)
    axarr[1, 0].set_title('Axis [1,0]')
    axarr[1, 1].scatter(x, y ** 2)
    axarr[1, 1].set_title('Axis [1,1]')
    """
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # draw lines
    xmin = 1
    xmax = 9
    y = 5
    height = 1

    plt.hlines(y, xmin, xmax)
    plt.vlines(xmin, y - height / 2., y + height / 2.)
    plt.vlines(xmax, y - height / 2., y + height / 2.)

    # draw a point on the line
    px = 4
    plt.plot(px, y, 'ro', ms=15, mfc='r')
    """


def plot_gridSearch_log(fname):
    """Docstring."""
    l = depickleLogFile(fname)
    ls = []
    for name in l['Disk A log']:
        if 'Chi2' not in name:
            p = l['Disk A log'][name]
            p_range = [min(p), max(p)]

            best_vals = [i for i in l['Best Fit A'][name]]
            print name
            print p_range
            print best_vals
            print
            print
            row = {'name': name,
                   'range': p_range,
                   'best_vals': best_vals}
            ls.append(row)
    df = pd.DataFrame(ls)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    p_min, p_max = df['range'][0]
    ax.set_xlim(p_min - 0.1*p_max, p_max + 0.1*p_max)

    y = 3
    height = 1

    plt.hlines(y, p_min, p_max)
    plt.vlines(p_min, y - height / 2., y + height / 2.)
    plt.vlines(p_max, y - height / 2., y + height / 2.)

    colors = ['r', 'b', 'g']
    for i in range(len(df['best_vals'])-1):
        plt.plot(df['best_vals'][i], y, marker='o', color=colors[i])  # , ms=15, mfc='r')

    plt.text(p_min - 0.1, y, p_min, horizontalalignment='right')
    plt.text(p_max + 0.1, y, p_max, horizontalalignment='left')

    plt.title(df['name'][0])
    ax.get_yaxis().set_visible(False)
    plt.show()


def plot_rolling_avg(dataPath):
    """Get an SMA for some data."""
    data = pd.read_csv(dataPath, sep=',')
    xs = data['step']
    ys = data['duration']/60

    colors = ['red', 'blue', 'green', 'yellow', 'orange']
    ns = [10, 20, 50]

    def get_rolling_avg(xs, ys, n):
        avg_ys = []
        for i in range(n/2, len(ys) - n/2):
            avg_y = sum(ys[i-n/2:i+n/2])/n
            avg_ys.append(avg_y)
        return avg_ys

    plt.plot(xs, ys, '-k', alpha=0.4, linewidth=0.1)
    for i in range(len(ns)):
        n = ns[i]
        avg_ys = get_rolling_avg(xs, ys, n)
        plt.plot(xs[n/2:-n/2], avg_ys, linestyle='-', color=colors[i],
                 linewidth=0.1 * n, label=str(n) + 'step smoothing')
    plt.legend()
    plt.xlabel('Step')
    plt.ylabel('Time (minutes)')
    plt.show(block=False)
