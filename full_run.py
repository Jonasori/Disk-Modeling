
# Basically just choose run method. This should be the last step in the chain.

import numpy as np
from grid_search import gridSearch, fullRun
from run_params import diskAParams, diskBParams



# Which method?

gs = True

if gs:
    fullRun(diskAParams, diskBParams)

else:
    mcmc.fullRun()


