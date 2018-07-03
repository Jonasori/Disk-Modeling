"""Basically just choose run method. This should be the last step in the chain.

blah.
"""

import subprocess as sp

# Local package files
from grid_search import fullRun
from run_params import diskAParams, diskBParams
from constants import today


# Which line are we looking at, and how are we fitting?
gs = True


if gs:
    # Set up a symlink to the /scratch directory to dump the model files to.
    print "Making new directories and setting up symlink."

    # Maybe a little bit janky
    scratch_dir = '/scratch/jonas/run_' + today
    sp.call(['rm', '-rf', scratch_dir, './models/run_', today])

    sp.call(['mkdir', scratch_dir])
    sp.call(['ln', '-s', scratch_dir, './models/'])
    sp.call(['touch', 'test.txt'])

    print "Starting fullRun"
    fullRun(diskAParams, diskBParams)

else:
    mcmc.fullRun()
