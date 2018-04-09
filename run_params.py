
# Parameters for the run


import numpy as np

"""
# Big run values
TatmsA = np.arange(50, 300, 50)
TqqA = -1 * np.arange(-0.4, 1., 0.3)
XmolA = -1 * np.arange(2, 7, 1.)
RAoutA = np.arange(350, 650, 60)
PAA = np.array([250])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.arange(20, 130, 30)
TqqB = -1 * np.arange(-0.4, 1., 0.3)
XmolB = -1 * np.arange(5., 11., 1.)
RAoutB = np.arange(70, 310, 60)
PAB = np.array([135])
InclB = np.array([30])
"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# Short test run values
TatmsA = np.array([300])
TqqA = -1 * np.array([-0.5])
XmolA = -1 * np.array([6.])
RAoutA = np.array([300])
PAA = np.array([250])
InclA = np.array([65])

# Parameters for Disk B
TatmsB = np.array([200])
TqqB = -1 * np.array([-0.6])
XmolB = -1 * np.array([7.])
RAoutB = np.array([200])
PAB = np.array([135])
InclB = np.array([30])






# Changed position angle B to have it move the right direction




diskAParams = np.array([TatmsA, TqqA, XmolA, RAoutA, PAA, InclA])
diskBParams = np.array([TatmsB, TqqB, XmolB, RAoutB, PAB, InclB])
