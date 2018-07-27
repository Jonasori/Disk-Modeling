"""
Some sets of parameters to be grid searching over.

Only fit atmsT, Xmol, RA
"""

import numpy as np


# Big run values

TatmsA = np.arange(10, 300, 50)
TqqA = np.arange(-3., 3, 1)
XmolA = -1 * np.arange(3, 11, 1.5)
R_outA = np.arange(200, 600, 50)
# PA and InclA are from Williams et al
PAA = np.array([69.7])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.arange(20, 240, 50)
TqqB = np.arange(-3., 3, 1)
XmolB = -1 * np.arange(1., 8., 1.5)
R_outB = np.arange(10, 260, 60)
PAB = np.array([135])
InclB = np.array([45])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Short test run values

# Parameters for Disk A
"""
TatmsA = np.array([300])
TqqA = -1 * np.array([-0.5])
XmolA = -1 * np.array([6.])
R_outA = np.array([300])
# PA and InclA are from Williams et al
PAA = np.array([69.7])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.array([200])
TqqB = -1 * np.array([-0.6])
XmolB = -1 * np.array([7.])
R_outB = np.array([200])
PAB = np.array([135])
InclB = np.array([30])
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Medium-length test run values
"""
# Parameters for Disk B
TatmsA = np.array([10, 50, 100, 200])
# TqqA = -1 * np.array([0.5])
TqqA = np.array([-0.5, 0.5])
XmolA = -1 * np.array([3., 4., 6., 8.])
R_outA = np.array([50, 200, 400, 600])
# PA and InclA are from Williams et al
PAA = np.array([69.7])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.array([10, 50, 100, 200])
# TqqB = -1 * np.array([-0.6, -0.9])
TqqB = np.array([-0.5])
XmolB = -1 * np.array([3., 4., 6., 8.])
R_outB = np.array([10, 50, 150, 300])
PAB = np.array([135])
InclB = np.array([30])
"""

diskAParams = np.array([TatmsA, TqqA, XmolA, R_outA, PAA, InclA])
diskBParams = np.array([TatmsB, TqqB, XmolB, R_outB, PAB, InclB])
