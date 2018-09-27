"""Basically just choose run method. This should be the last step in the chain.

blah.
"""

import subprocess as sp

# Local package files
from grid_search import fullRun
from run_params import diskAParams, diskBParams
from constants import today
from tools import already_exists, remove


# Which fitting method?
gs = True


if gs:
    fullRun(diskAParams, diskBParams)


# if mc:
#     mcmc.fullRun()
