"""Basically just choose run method. This should be the last step in the chain.

blah.
"""

import subprocess as sp

# Local package files
from grid_search import fullRun
from run_params import diskAParams, diskBParams
from constants import today
from tools import already_exists


# Which line are we looking at, and how are we fitting?
gs = True


if gs:
    # Set up a symlink to the /scratch directory to dump the model files to.
    print "Making new directories and setting up symlink."

    # A little bit janky
    scratch_home = '/scratch/jonas/'
    this_run_basename = today

    counter = 2
    this_run = this_run_basename
    while already_exists(scratch_home + this_run) is True:
        this_run = this_run_basename + '-' + str(counter)
        counter += 1

    scratch_dir = scratch_home + this_run

    # Cool. Now we know where we're symlinking to.
    modelPath = './models/' + this_run + '/' + this_run

    sp.call(['rm', '-rf', '{}'.format(modelPath)])
    sp.call(['rm', '-rf', scratch_dir])

    sp.call(['mkdir', scratch_dir])
    sp.call(['ln', '-s', scratch_dir, './models/'])

    print "Starting fullRun"
    fullRun(diskAParams, diskBParams, )


else:
    mcmc.fullRun()
