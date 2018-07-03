"""Basically just choose run method. This should be the last step in the chain.

blah.
"""

import datetime
import subprocess as sp
from grid_search import fullRun
from run_params import diskAParams, diskBParams


# Which line are we looking at, and how are we fitting?
mol = 'hco'
gs = True

# What day is it? Used to ID files.
months = ['jan', 'feb', 'march', 'april', 'may',
          'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']
td = datetime.datetime.now()
today = months[td.month - 1] + str(td.day)


if gs:
    # Set up a symlink to the /scratch directory to dump the model files to.
    print "Making new directories and setting up symlink."
    # Watch out: -p is overwrite, so that'll delete everything in the directory
    # if there's already one there.
    scratch_dir = '/scratch/jonas/run_' + today
    sp.call(['mkdir', '-p', scratch_dir])
    sp.call(['ln', '-s', '{} ./models/'.format(scratch_dir)])

    print "Starting fullRun"
    fullRun(diskAParams, diskBParams)

else:
    mcmc.fullRun()
