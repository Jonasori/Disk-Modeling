"""Run the ICR process while cutting off baselines below b_max.

Testing a change.
"""

import subprocess as sp
import numpy as np
import matplotlib.pyplot as plt
import argparse as ap
import pandas as pd
from tools import icr, imstat

# baselines = [i*20 for i in range(1, 5)]
baselines = np.arange(0, 150, 5)
dfile = 'data-hco'


def main():
    """Run it."""
    parser = ap.ArgumentParser(formatter_class=ap.RawTextHelpFormatter,
                               description='''Make a run happen.''')

    parser.add_argument('-r', '--run',
                        action='store_true',
                        help='Run the analysis.')
    args = parser.parse_args()

    if args.run:
        run(dfile)


def get_baseline_rmss(modelName, baselines=baselines, remake_all=False):
    """Iterate through a range of baseline cutoffs and compare the results.

    Args:
        modelName (str): the name of the core data file that this is pulling.
        baselines (list of ints): the baselines to check over.
        remake_all (bool): if True, re-convolve all files, overwriting
                           pre-existing files if need be.
    """
    data_list = []
    for b in baselines:
        print '\n\n\n    NEW ITERATION\nBaseline: ', b, '\n'
        if b == 0:
            name = modelName
        else:
            name = modelName + str(b)

        # Check if we've already icr'ed this one.
        if name in sp.check_output(['ls']) and remake_all is False:
            print "File already exists; going straight to imstat"
            mean, rms = imstat(name)

        # If not, get rms, clean down to it.
        else:
            print "Starting dirty clean"
            # do a dirty clean to get the rms value to clean down to.
            icr(modelName, min_baseline=b, niters=1)
            mean, rms = imstat(name)
            print "Dirty rms is", rms
            # Now do a real clean
            mean, rms = imstat(name)
            icr(modelName, min_baseline=b, rms=0.5*rms)

        step_output = {'RMS': rms,
                       'Mean': mean,
                       'Baseline': b}

        data_list.append(step_output)
        print step_output

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
    plt.savefig('noise_by_baselines.png')
    # plt.show(block=False)
    return [df['Baseline'], df['Mean'], df['RMS']]


def run(modelName, Baselines=baselines):
    """Run the above functions."""
    ds = get_baseline_rmss(modelName, Baselines)
    analysis(ds)


if __name__ == '__main__':
    main()


# The End
