"""Run the ICR process while cutting off baselines below b_max."""

import subprocess as sp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

baselines = [i*5 for i in range(1, 30)]
dfile = 'data-hco'


def icr_w_baselines(modelName, b_max):
    """Run the normal icr() but with a uvrange argument in invert."""
    print "\nEntering icr()\n"
    sp.call('rm -rf {}.mp'.format(modelName + str(b_max)), shell=True)
    sp.call('rm -rf {}.bm'.format(modelName + str(b_max)), shell=True)
    sp.call('rm -rf {}.cl'.format(modelName + str(b_max)), shell=True)
    sp.call('rm -rf {}.cm'.format(modelName + str(b_max)), shell=True)

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


def imstat(modelName, b_max=''):
    """Find rms and mean.

    Want an offsource region so that we can look at the noise.
    """
    r_offsource = '(-3,-3,-1,-1)'
    print '\n\n IMSTATING ', modelName + str(b_max)
    imstat_out = sp.check_output(['imstat',
                                  'in={}.cm'.format(modelName + str(b_max)),
                                  'region=arcsec,box{}'.format(r_offsource)
                                  ])

    # Just return the last chunk of text and figure out what to do w/ it later
    return imstat_out[-140:]


def find_baseline_cutoff(modelName, baselines):
    """Iterate through a range of baseline cutoffs and compare the results."""
    raw_data_list = []
    for b in baselines:
        print '\n\n\n'
        print '    NEW ITERATION'
        print 'Baseline: ', b
        print '\n\n'

        icr_w_baselines(modelName, b)
        imstat_data = imstat(modelName, b)
        step_output = {'Data': imstat_data,
                       'Baseline': str(b)}

        raw_data_list.append(step_output)

    raw_data_pd = pd.DataFrame(raw_data_list)
    return raw_data_pd


def analysis(df):
    """Read the df from find_baseline_cutoff and do cool shit with it."""
    means = []
    rmss = []
    baselines = []
    for b, d in zip(df['Baseline'], df['Data']):

        print float(d[91:101]), float(d[102:111])

        # Grab the chunk of the string giving the mean and rms signal
        means.append(float(d[91:101]))
        rmss.append(float(d[102:111]))
        baselines.append(float(b))

    f, axarr = plt.subplots(2, sharex=True)
    axarr[0].grid(axis='x')
    axarr[0].set_title('RMS Noise')
    axarr[0].ylabel('RMS Off-Source Flux (Jy/Beam)')
    axarr[0].plot(baselines, rmss)

    axarr[1].grid(axis='x')
    axarr[1].set_title('Mean Noise')
    axarr[1].ylabel('Mean Off-Source Flux (Jy/Beam)')
    axarr[1].xlabel('Baseline (kilalambda)')
    axarr[1].plot(baselines, means)
    plt.savefig('baseline_analysis.png')
    plt.show(block=False)
    return [baselines, means, rmss]


def run(modelName, Baselines=baselines):
    ds = find_baseline_cutoff(modelName, Baselines)
    analysis(ds)


def sqrt(N, nsteps=5):
    """Docstring."""
    x = 0.5 * N
    for i in range(nsteps):
        x_new = 0.5 * (x + N/x)
        x = x_new
    return x

# The End
