
# Parameters for the run


import numpy as np


# Big run values
"""
TatmsA = np.arange(10, 300, 50)
TqqA = -1 * np.arange(-1., 4, 0.7)
XmolA = -1 * np.arange(3, 9, 1.)
RAoutA = np.arange(200, 400, 40)
# PA and InclA are from Williams et al
PAA = np.array([69.7])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.arange(20, 240, 50)
TqqB = -1 * np.arange(-1, 4., 0.7)
XmolB = -1 * np.arange(3., 9., 1.)
RAoutB = np.arange(20, 250, 60)
PAB = np.array([135])
InclB = np.array([45])
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Short test run values


# Parameters for Disk A
"""
TatmsA = np.array([300])
TqqA = -1 * np.array([-0.5])
XmolA = -1 * np.array([6.])
RAoutA = np.array([300])
PAA = np.array([250])
InclA = np.array([65, 70])

# Parameters for Disk B
TatmsB = np.array([200])
TqqB = -1 * np.array([-0.6])
XmolB = -1 * np.array([7.])
RAoutB = np.array([200])
PAB = np.array([135])
InclB = np.array([30, 60])
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Medium-length test run values

# Parameters for Disk B
TatmsA = np.array([100, 300, 500])
TqqA = -1 * np.array([-0.5, -0.7, -1.])
XmolA = -1 * np.array([6., 7.5, 9.])
RAoutA = np.array([200, 400, 600])
PAA = np.array([250])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.array([200, 400])
TqqB = -1 * np.array([-0.6, -0.9])
XmolB = -1 * np.array([7., 9.])
RAoutB = np.array([200, 400])
PAB = np.array([135])
InclB = np.array([30])





# Changed position angle B to have it move the right direction




diskAParams = np.array([TatmsA, TqqA, XmolA, RAoutA, PAA, InclA])
diskBParams = np.array([TatmsB, TqqB, XmolB, RAoutB, PAB, InclB])
