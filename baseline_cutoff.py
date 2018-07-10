"""Run the ICR process while cutting off baselines below b_max.

Testing a change.
"""

import subprocess as sp
import numpy as np
import matplotlib.pyplot as plt
import argparse as ap
import pandas as pd
from tools import icr, imstat, already_exists


baselines = np.arange(0, 130, 5)


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
        run(remake_all=False, Baselines=baselines,
            niters=1e4, mol='hco')

    elif args.run_and_overwrite:
        run(remake_all=False, Baselines=baselines,
            niters=1e4, mol='hco')


def get_baseline_rmss(mol, niters=1e4, baselines=baselines, remake_all=False):
    """Iterate through a range of baseline cutoffs and compare the results.

    Args:
        vis (str): the name of the core data file that this is pulling.
        baselines (list of ints): the baselines to check over.
        remake_all (bool): if True, re-convolve all files, overwriting
                           pre-existing files if need be.
    """
    # Set up the symlink
    run_dir = './baselines/baseline_' + mol + str(int(niters)) + '/'
    scratch_dir = '/scratch/jonas/' + run_dir
    orig_vis = './data/' + mol + '/' + mol
    new_vis = run_dir + mol

    sp.call(['rm -rf {}'.format(scratch_dir)], shell=True)
    # :-1 because a symlink with a deleted root isn't a directory anymore
    sp.call(['rm -rf {}'.format(run_dir[:-1])], shell=True)

    sp.call(['mkdir {}'.format(scratch_dir)], shell=True)
    sp.call(['ln', '-s', scratch_dir, './baselines/'])

    sp.call(['cp', '-r', '{}.vis'.format(orig_vis),
             '{}/'.format(run_dir)])

    print "Made symlinked directory, copied core .vis over.\n\n"

    data_list = []
    for b in baselines:
        print '\n\n\n    NEW ITERATION\nBaseline: ', b, '\n'
        if b == 0:
            name = run_dir + mol
        else:
            name = run_dir + mol + str(b)
        print name

        # If we want to reconvolve everything, then start by deleting them.
        if remake_all is True:
            sp.call(['rm', '-rf', '{}.{{cm, cl, mp, bm}}'.format(name)])

        if b == 0:
            print "Don't delete the 0-baseline you stoop!"
            mean, rms = imstat(name + '.vis')

        # Check if we've already icr'ed this one.
        elif name + '.cm' in sp.check_output(['ls']):
            print "File already exists; going straight to imstat"
            mean, rms = imstat(name + '.vis')

        # If not, get rms, clean down to it.
        else:
            icr(new_vis, min_baseline=b, niters=niters)
            mean, rms = imstat(name + '.vis')

        step_output = {'RMS': rms,
                       'Mean': mean,
                       'Baseline': b}

        data_list.append(step_output)
        print step_output

    data_pd = pd.DataFrame(data_list)
    return data_pd


def analysis(df, mol, niters):
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
    im_name = 'imnoise_' + mol + str(int(niters)) + '.png'
    plt.savefig(im_name)
    # plt.show(block=False)
    return [df['Baseline'], df['Mean'], df['RMS']]


def run(remake_all=True, baselines=baselines, niters=1e4, mol='hco'):
    """Run the above functions."""
    ds = get_baseline_rmss(mol, niters, baselines, remake_all)
    analysis(ds, mol, niters)


if __name__ == '__main__':
    main()




# The End
