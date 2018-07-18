"""Analysis.

Some plotting and other analysis functions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import subprocess as sp
import seaborn as sns
from constants import today


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


def plot_gridSearch_log(fname):
    """Plot where the best-fit values from a grid search fall.

    Takes in the pickled step log from the grid search,
    plots where the best-fit value(s) stand(s) relative to the range queried

    Make xticks([unique(Disk A log)])
    """
    # Grab the values to distribute
    df = depickleLogFile(fname)

    del df['Disk A log']['Reduced Chi2']
    del df['Disk A log']['Raw Chi2']

    disk_A, disk_B = [], []
    [disk_A.append({}) for i in df['Disk A log']]
    [disk_B.append({}) for i in df['Disk A log']]

    for i, p in enumerate(df['Disk A log']):
        if p != 'Raw Chi2' and p != 'Reduced Chi2':

            ps_A = df['Disk A log'][p]
            disk_A[i]['p_min'] = min(ps_A)
            disk_A[i]['p_max'] = max(ps_A)
            disk_A[i]['best_fits'] = list(df['Best Fit A'][p])
            disk_A[i]['xvals_queried'] = list(set(ps_A))
            disk_A[i]['name'] = p

            ps_B = df['Disk B log'][p]
            disk_B[i]['p_min'] = min(ps_B)
            disk_B[i]['p_max'] = max(ps_B)
            disk_B[i]['best_fits'] = list(df['Best Fit B'][p])
            disk_B[i]['xvals_queried'] = list(set(ps_B))
            disk_B[i]['name'] = p
    both_disks = [disk_A, disk_B]

    # Plot out
    colors = ['red', 'blue']
    f, axarr = plt.subplots(len(disk_A), 2)
    for d in [0, 1]:
        params = both_disks[d]
        for i, p in enumerate(params):
            xs = np.linspace(p['p_min'], p['p_max'], 2)
            axarr[i, d].set_title(p['name'])
            axarr[i, d].yaxis.set_ticks([])
            axarr[i, d].xaxis.set_ticks(p['xvals_queried'])
            axarr[i, d].plot(xs, [0]*2, '-k')
            for bf in p['best_fits']:
                a = 1/(len(p['best_fits']))
                axarr[i, d].plot(bf, 0, marker='o', color=colors[d], alpha=a)

    plt.tight_layout()
    plt.savefig(fname + 'results.png')
    plt.show(block=False)


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
