"""
Some sets of parameters to be grid searching over.

Only fit atmsT, Xmol, RA
"""

import numpy as np


# Big run values
"""
TatmsA = np.arange(10, 300, 50)
TqqA = -1 * np.arange(-1., 4, 0.7)
XmolA = -1 * np.arange(3, 9, 1.)
R_outA = np.arange(200, 400, 40)
# PA and InclA are from Williams et al
PAA = np.array([69.7])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.arange(20, 240, 50)
TqqB = -1 * np.arange(-1, 4., 0.7)
XmolB = -1 * np.arange(3., 9., 1.)
R_outB = np.arange(20, 250, 60)
PAB = np.array([135])
InclB = np.array([45])
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Short test run values

# Parameters for Disk A

TatmsA = np.array([300])
TqqA = -1 * np.array([-0.5])
XmolA = -1 * np.array([6.])
R_outA = np.array([300])
PAA = np.array([250])
InclA = np.array([65, 70])

# Parameters for Disk B
TatmsB = np.array([200])
TqqB = -1 * np.array([-0.6])
XmolB = -1 * np.array([7.])
R_outB = np.array([200])
PAB = np.array([135])
InclB = np.array([30, 60])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Medium-length test run values
"""
# Parameters for Disk B
TatmsA = np.array([10, 75, 150, 300])
# TqqA = -1 * np.array([-0.5, -0.7, -1.])
TqqA = np.array([-1.1, -0.7, -0.1, 0.5])
XmolA = -1 * np.array([6., 8., 10., 12.])
R_outA = np.array([50, 200, 400, 600])
PAA = np.array([250])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.array([1, 10, 75, 150])
# TqqB = -1 * np.array([-0.6, -0.9])
TqqB = np.array([-0.7])
XmolB = -1 * np.array([4., 6., 8., 10.])
R_outB = np.array([50, 200, 400, 600])
PAB = np.array([135])
InclB = np.array([30])
"""



diskAParams = np.array([TatmsA, TqqA, XmolA, R_outA, PAA, InclA])
diskBParams = np.array([TatmsB, TqqB, XmolB, R_outB, PAB, InclB])
