"""Basically just choose run method. This should be the last step in the chain.

blah.
"""

import subprocess as sp

# Local package files
from grid_search import fullRun
from run_params import diskAParams, diskBParams
from constants import today
from tools import already_exists, remove


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

    # Cool. Now we know where we're symlinking to.
    scratch_dir = scratch_home + this_run

    # remove(modelPath)
    # remove(scratch_dir)

    sp.call(['mkdir', scratch_dir])
    sp.call(['ln', '-s', scratch_dir, './models/'])

    print "Starting fullRun"

    # Give the grid search the path to be dumping things into.
    modelPath = './models/' + this_run + '/' + this_run
    fullRun(diskAParams, diskBParams, modelPath)


# else:
#     mcmc.fullRun()
