"""
Some sets of parameters to be grid searching over.

Only fit atmsT, Xmol, RA
"""

import numpy as np
from constants import offsets, vsys
"""
# Offset vals from original fitting
pos_Ax = -0.0298
pos_Ay = 0.072
pos_Bx = -1.0456
pos_By = -0.1879
"""

# Fit offset vals:
pos_Ax = offsets[0][0]
pos_Ay = offsets[0][1]

pos_Bx = offsets[1][0]
pos_By = offsets[1][1]

vsysA = vsys[0]
vsysB = vsys[1]


# Big run values
"""
TatmsA    = np.arange(10, 500, 100)
# TqqA    = -1 * np.array([0.5])
TqqA      = np.arange(-1, 2, 0.5)
XmolA     =  -1 * np.arange(4., 13., 2)
R_outA    = np.arange(100, 600, 100)
# PA and InclA are from Williams et al
PAA       = np.array([69.7])
InclA     = np.array([65])
Pos_XA    = np.array([pos_Ax])
Pos_YA    = np.array([pos_Ay])
VsysA     = np.array([vsysA])

# Parameters for Disk B
TatmsB    = np.arange(10, 500, 100)
TqqB      = np.arange(-1, 2, 0.5)
XmolB     = -1 * np.arange(4., 13., 2)
R_outB    = np.arange(10, 400, 100)
PAB       = np.array([135])
InclB     = np.array([45])
Pos_XB    = np.array([pos_Bx])
Pos_YB    = np.array([pos_By])
VsysB     = np.array([10.70])

"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Medium-length test run values
"""
# Parameters for Disk B
TatmsA    = np.arange(100, 700, 200)
# TqqA    = -1 * np.array([0.5])
TqqA      = np.array([-1., 0., 1.])
XmolA     =  -1 * np.arange(6., 13., 2)
R_outA    = np.arange(100, 700, 200)
# PA and InclA are from Williams et al
PAA       = np.array([69.7])
InclA     = np.array([30, 45, 60, 75])
Pos_XA    = np.array([pos_Ax])
Pos_YA    = np.array([pos_Ay])
VsysA     = np.array([vsysA])

# Parameters for Disk B
TatmsB    = np.arange(100, 700, 200)
TqqB      = np.array([-1., 0., 1.])
XmolB     = -1 * np.arange(6., 13., 2)
R_outB    = np.arange(50, 400, 150)
PAB       = np.array([135])
InclB     = np.array([45])
Pos_XB    = np.array([pos_Bx])
Pos_YB    = np.array([pos_By])
VsysB     = np.array([vsysB])
"""


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Short test run values

# Parameters for Disk A
"""
TatmsA    = np.array([300])
TqqA      = -1 * np.array([-0.5])
XmolA     = -1 * np.array([6.])
R_outA    = np.array([300])
# PA and InclA are from Williams et al
PAA       = np.array([69.7])
InclA     = np.array([65])
Pos_XA    = np.array([pos_Ax])
Pos_YA    = np.array([pos_Ay])
VsysA     = np.array([vsysA])


# Parameters for Disk B
TatmsB    = np.array([200])
TqqB      = -1 * np.array([-0.6])
XmolB     = -1 * np.array([7.])
R_outB    = np.array([200])
PAB       = np.array([135])
InclB     = np.array([30])
Pos_XB    = np.array([pos_Bx])
Pos_YB    = np.array([pos_By])
VsysB     = np.array([vsysB])

"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Offset fitting values
# Parameters for Disk A
#"""
TatmsA    = np.array([300])
TqqA      = -1 * np.array([-0.5])
XmolA     = -1 * np.array([8.])
R_outA    = np.array([300])
# PA and InclA are from Williams et al
PAA       = np.array([69.7])
InclA     = np.array([65])
# Pos_XA    = np.array([pos_Ax])
# Pos_YA    = np.array([pos_Ay])
# VsysA     = np.array([vsysA])
Pos_XA    = np.arange(pos_Ax - 0.1, pos_Ax + 0.1, 0.05)
Pos_YA    = np.arange(pos_Ay - 0.1, pos_Ay + 0.1, 0.05)
VsysA     = np.arange(vsysA - 0.11, vsysA + 0.1, 0.03)

# Parameters for Disk B
TatmsB    = np.array([150])
TqqB      = -1 * np.array([-0.6])
XmolB     = -1 * np.array([10.])
R_outB    = np.array([100])
PAB       = np.array([135])
InclB     = np.array([30])
# Pos_XB    = np.array([pos_Bx])
# Pos_YB    = np.array([pos_By])
# VsysB     = np.array([10.69])
Pos_XB    = np.arange(pos_Bx - 0.1, pos_Bx + 0.1, 0.05)
Pos_YB    = np.arange(pos_By - 0.1, pos_By + 0.1, 0.05)
VsysB     = np.arange(vsysB - 0.11, vsysB + 0.1, 0.03)
#"""






diskAParams = np.array([TatmsA, TqqA, XmolA, R_outA, PAA, InclA, Pos_XA, Pos_YA, VsysA])
diskBParams = np.array([TatmsB, TqqB, XmolB, R_outB, PAB, InclB, Pos_XB, Pos_YB, VsysB])
