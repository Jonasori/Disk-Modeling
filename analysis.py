"""Functions to analyze and plot output from a gridSearch run.

Some thoughts:
    - All of them (so far) have

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import subprocess as sp
import seaborn as sns


def depickleLogFile(filename):
    """Read in the pickle'd full-log file from a run.

    Could reorganize this and plot_gridSearch_log make this more of an
    unpacking function and that to be more of a plotter, i.e. moving the first
    23 lines of plot_gridSearch_log here.
    """
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

    X2s = [out['Disk A log']['Raw Chi2'], out['Disk A log']['Reduced Chi2']]
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
            disk_B[i]['best_fits'] = list(out['Best Fit B'][p])
            disk_B[i]['xvals_queried'] = list(set(ps_B))
            disk_B[i]['name'] = p

    both_disks = [disk_A, disk_B]
    return both_disks


def plot_gridSearch_log(fname):
    """Plot where the best-fit values from a grid search fall.

    Plot where the best-fit value(s) stand(s) relative to the range queried in
    a given grid search run.

    Args:
        fname (str): Name of the pickled step log from the grid search.
        Assumes fname is './models/run_dateofrun/dateofrun'
    """
    # Grab the values to distribute
    df = depickleLogFile(fname)

    X2s = [df['Disk A log']['Raw Chi2'], df['Disk A log']['Reduced Chi2']]
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
    both_disks = depickleLogFile

    # Plot out
    colors = ['red', 'blue']
    f, axarr = plt.subplots(len(disk_A) + 1, 2, figsize=[5, 6])
    # f, axarr = plt.subplots(len(disk_A), 2, figsize=[5, 8])
    # Add the text info
    axarr[0, 0].axis('off')
    axarr[0, 1].axis('off')
    axarr[0, 0].text(0, 0, "Test string", fontsize=14, fontweight='bold')
    axarr[0, 1].text(0, 0, "Test string", fontsize=14, fontweight='bold')
    # Plot the number lines
    for d in [0, 1]:
        params = both_disks[d]
        for i, p in enumerate(params, 1):
            # for i, p in enumerate(params):
            xs = np.linspace(p['p_min'], p['p_max'], 2)
            # axarr[i, d].get_xaxis().set_visible(False)
            axarr[i, d].set_title(p['name'])
            axarr[i, d].yaxis.set_ticks([])
            axarr[i, d].xaxis.set_ticks(p['xvals_queried'])
            axarr[i, d].plot(xs, [0]*2, '-k')
            for bf in p['best_fits']:
                a = 1/(len(p['best_fits']))
                axarr[i, d].plot(bf, 0, marker='o', color=colors[d], alpha=a)

    plt.tight_layout()
    # sns.despine()
    # plt.savefig('./models/' + fname.split('/')[-1] + 'results.png')
    plt.show(block=False)


def plot_step_duration(dataPath, ns=[10, 20, 50]):
    """Plot how long each step took, plus some smoothing stuff.

    Args:
        dataPath (str): Path to the run we want to analyze, plus base name,
                        i.e. './models/run_dateofrun/dateofrun'
        ns (list of ints): A list of the smoothing windows to use.
                           Note len(ns) can't be longer than 5 without adding
                           more colors to colors list.
    """
    data = pd.read_csv(dataPath + '_stepDurations.csv', sep=',')
    xs = data['step']
    ys = data['duration']/60

    def get_rolling_avg(xs, ys, n):
        avg_ys = []
        for i in range(n/2, len(ys) - n/2):
            avg_y = sum(ys[i-n/2:i+n/2])/n
            avg_ys.append(avg_y)
        return avg_ys

    plt.plot(xs, ys, '-k', alpha=0.9, linewidth=0.1, label='True Time')

    colors = ['orange', 'red', 'blue', 'green', 'yellow']
    for i in range(len(ns)):
        n = ns[i]
        avg_ys = get_rolling_avg(xs, ys, n)
        plt.plot(xs[n/2:-n/2], avg_ys, linestyle='-', color=colors[i],
                 linewidth=0.1 * n, label=str(n) + 'step smoothing')

    run_date = dataPath.split('/')[-1]
    plt.legend()
    plt.xlabel('Step')
    plt.ylabel('Time (minutes)')
    plt.title('Time per Step for Grid Search Run on ' + run_date)
    plt.show(block=False)
