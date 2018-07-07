"""Run the ICR process while cutting off baselines below b_max.

Testing a change.
"""

import subprocess as sp
import numpy as np
import matplotlib.pyplot as plt
import argparse as ap
import pandas as pd
from tools import icr, imstat, already_exists

# baselines = [i*20 for i in range(1, 5)]
# baselines = np.arange(0, 130, 10)
baselines = np.sort(np.concatenate((np.arange(0, 130, 10),
                                    np.arange(55, 125, 10)
                                    )))

baselines = np.arange(10, 130, 5)

mol = 'hco'
dfile = 'data/' + mol + '/' + mol
niters = 1e4

def main():
    """Run it."""
    parser = ap.ArgumentParser(formatter_class=ap.RawTextHelpFormatter,
                               description='''Make a run happen.''')

    parser.add_argument('-r', '--run',
                        action='store_true',
                        help='Run the analysis.')

    parser.add_argument('-o', '--run_and_overwrite',
                        action='store_true',
                        help='Run the analysis, overwriting preexisting runs.')

    args = parser.parse_args()
    if args.run:
        run(dfile, remake_all=False)
    elif args.run_and_overwrite:
        run(dfile, remake_all=True)


def get_baseline_rmss(modelName, baselines=baselines, remake_all=False):
    """Iterate through a range of baseline cutoffs and compare the results.

    Args:
        modelName (str): the name of the core data file that this is pulling.
        baselines (list of ints): the baselines to check over.
        remake_all (bool): if True, re-convolve all files, overwriting
                           pre-existing files if need be.
    """

    # Set up the symlink
    run = 'baselines_' + mol + str(niters)
    scratch_dir = '/scratch/jonas/' + run

    # If we're remaking everything, just wipe it out.
    if remake_all is True:
        sp.call(['rm -rf {}'.format(scratch_dir)])
        sp.call(['rm -rf ./baselines/{}'.format(run)])

    # If we're not remaking everything, then check if it's already there.
    # If not, make a new symlink
    if already_exists(scratch_dir) is False:
        sp.call(['mkdir', scratch_dir])
        sp.call(['ln', '-s', scratch_dir, './baselines/'])

    sp.call(['cp {}'.format(dfile), './baselines/{}'.format(run)])

    data_list = []
    for b in baselines:
        print '\n\n\n    NEW ITERATION\nBaseline: ', b, '\n'
        if b == 0:
            name = modelName
        else:
            name = modelName + str(b)
        print name

        # If we want to reconvolve everything, then start by deleting them.
        if remake_all is True:
            sp.call(['rm', '-rf', '{}.{{cm, cl, mp, bm}}'.format(name)])

        if b == 0:
            print "Don't delete the 0-baseline you stoop!"
            mean, rms = imstat(name)

        # Check if we've already icr'ed this one.
        elif name + '.cm' in sp.check_output(['ls']):
            print "File already exists; going straight to imstat"
            mean, rms = imstat(name)

        # If not, get rms, clean down to it.
        else:
            # Now do a real clean
            icr(modelName, min_baseline=b, niters=niters)
            mean, rms = imstat(name)

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
    # axarr[0].plot(df['Baseline'], df['RMS'], 'or')
    axarr[0].plot(df['Baseline'], df['RMS'], '-b')

    axarr[1].grid(axis='x')
    axarr[1].set_title('Mean Noise')
    axarr[1].set_xlabel('Baseline length (k-lambda)')
    # axarr[1].set_ylabel('Mean Off-Source Flux (Jy/Beam)')
    # axarr[1].plot(df['Baseline'], df['Mean'], 'or')
    axarr[1].plot(df['Baseline'], df['Mean'], '-b')
    plt.savefig('noise_by_baselines.png')
    # plt.show(block=False)
    return [df['Baseline'], df['Mean'], df['RMS']]


def run(modelName, remake_all=False, Baselines=baselines):
    """Run the above functions."""
    ds = get_baseline_rmss(modelName, Baselines, remake_all)
    analysis(ds)


if __name__ == '__main__':
    main()




ln -s /scratch/jonas/scratch_dir ./test_local



# The End
