"""Run the ICR process while cutting off baselines below b_max.

Testing a change.
"""

import subprocess as sp
import numpy as np
import matplotlib.pyplot as plt
import argparse
import pandas as pd
from tools import icr
from tools import imstat

# baselines = [i*20 for i in range(1, 5)]
baselines = np.arange(40, 150, 5)
dfile = 'data-hco'



def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='''Make a run happen.''')

    parser.add_argument('-r', '--run', action='store_true', help='Run the analysis.')
    args = parser.parse_args()
    
    if args.run:
        run(dfile)




def get_baseline_rmss(modelName, baselines=baselines):
    """Iterate through a range of baseline cutoffs and compare the results."""
    data_list = []
    for b in baselines:
        print '\n\n\n'
        print '    NEW ITERATION'
        print 'Baseline: ', b
        print '\n\n'

	# Do a dirty clean to get the rms value to clean down to.
        print "Starting dirty clean"
        icr(modelName, min_baseline=b, niters=1)
        mean, rms = imstat(modelName + str(b))
        print "Dirty rms is", rms
	# Now do a real clean
	mean, rms = imstat(modelName + str(b))
	icr(modelName, min_baseline=b, rms=0.5*rms)
        step_output = {'RMS': rms,
                       'Mean': mean,
                       'Baseline': b}

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
    plt.savefig('noise_by_baselines.png')
    # plt.show(block=False)
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


if __name__ == '__main__':
    main()


# The End
