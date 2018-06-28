"""Run the ICR process while cutting off baselines below b_max.

Testing a change.
"""

import subprocess as sp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tools import imstat

baselines = [i*5 for i in range(1, 30)]
dfile = 'data-hco'


def icr_w_baselines(modelName, b_max):
    """Run the normal icr() but with a uvrange argument in invert."""
    print "\nEntering icr()\n"
    sp.call('rm -rf {}.{{mp, bm, cl, cm}}'.format(modelName + str(b_max)), shell=True)

    # Add restfreq to this vis
    sp.call(['puthd',
             'in={}.vis/restfreq'.format(modelName),
             'value=356.73422300'])

    sp.call(['invert',
             'vis={}.vis'.format(modelName),
             'map={}.mp'.format(modelName + str(b_max)),
             'beam={}.bm'.format(modelName + str(b_max)),
             'options=systemp',
             'cell=0.045',
             'select=-uvrange{}'.format((0, b_max)),
             'imsize=256',
             'robust=2'])

    sp.call(['clean',
             'map={}.mp'.format(modelName + str(b_max)),
             'beam={}.bm'.format(modelName + str(b_max)),
             'out={}.cl'.format(modelName + str(b_max)),
             'niters=10000',
             'threshold=1e-3'])

    sp.call(['restor',
             'map={}.mp'.format(modelName + str(b_max)),
             'beam={}.bm'.format(modelName + str(b_max)),
             'model={}.cl'.format(modelName + str(b_max)),
             'out={}.cm'.format(modelName + str(b_max))
             ])



def get_baseline_rmss(modelName, baselines=baselines):
    """Iterate through a range of baseline cutoffs and compare the results."""
    data_list = []
    for b in baselines:
        print '\n\n\n'
        print '    NEW ITERATION'
        print 'Baseline: ', b
        print '\n\n'

        icr_w_baselines(modelName, b)
        mean, rms = imstat(modelName + str(b))
        step_output = {'RMS': rms,
                       'Mean': mean,
                       'Baseline': str(b)}

        data_list.append(step_output)

    data_pd = pd.DataFrame(data_list)
    return data_pd


def analysis(df):
    """Read the df from find_baseline_cutoff and do cool shit with it."""
    f, axarr = plt.subplots(2, sharex=True)
    axarr[0].grid(axis='x')
    axarr[0].set_title('RMS Noise')
    # axarr[0].set_ylabel('RMS Off-Source Flux (Jy/Beam)')
    axarr[0].plot(df['Baseline'], df['RMS'])

    axarr[1].grid(axis='x')
    axarr[1].set_title('Mean Noise')
    # axarr[1].set_ylabel('Mean Off-Source Flux (Jy/Beam)')
    axarr[1].set_xlabel('Baseline length (k-lambda)')
    axarr[1].plot(df['Baseline'], df['Mean'])
    plt.savefig('baseline_analysis.png')
    plt.show(block=False)
    return [df['Baseline'], df['Mean'], df['RMS']]


def run(modelName, Baselines=baselines):
    """Run the above functions."""
    ds = get_baseline_rmss(modelName, Baselines)
    analysis(ds)


def sqrt(N, nsteps=5):
    """Docstring."""
    x = 0.5 * N
    for i in range(nsteps):
        x_new = 0.5 * (x + N/x)
        x = x_new
    return x

# The End
