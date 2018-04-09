
# Run a grid search


import os, sys, datetime
from disk import *
import raytrace as rt
from astropy.io import fits
import numpy as np
import subprocess as sp
import astropy.units as u
from utils import makeModel, sumDisks, chiSq
from run_params import diskAParams, diskBParams

# Velocity axes might be backwards
# options=3value csize=1,2
# Write into short log file how many steps were taken


# Data file name:
data_file = 'data-hco'



# Prep some storage space for all the chisq vals
"""
diskARawX2 = np.zeros((len(TatmsA), len(TqqA), len(XmolA), len(RAoutA), len(PAA), len(InclA)))
diskBRawX2 = np.zeros((len(TatmsB), len(TqqB), len(XmolB), len(RAoutB), len(PAB), len(InclB)))

diskARedX2 = np.zeros((len(TatmsA), len(TqqA), len(XmolA), len(RAoutA), len(PAA), len(InclA)))
diskBRedX2 = np.zeros((len(TatmsB), len(TqqB), len(XmolB), len(RAoutB), len(PAB), len(InclB)))
"""

diskARawX2 = np.zeros((len(diskAParams[0]), len(diskAParams[1]), len(diskAParams[2]), len(diskAParams[3]), len(diskAParams[4]), len(diskAParams[5])))
diskBRawX2 = np.zeros((len(diskBParams[0]), len(diskBParams[1]), len(diskBParams[2]), len(diskBParams[3]), len(diskBParams[4]), len(diskBParams[5])))

diskARedX2 = np.zeros((len(diskAParams[0]), len(diskAParams[1]), len(diskAParams[2]), len(diskAParams[3]), len(diskAParams[4]), len(diskAParams[5])))
diskBRedX2 = np.zeros((len(diskAParams[0]), len(diskBParams[1]), len(diskBParams[2]), len(diskBParams[3]), len(diskBParams[4]), len(diskBParams[5])))



# Name the output file
td = datetime.datetime.now()
months = ['jan', 'feb', 'march', 'april', 'may', 'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']
today = months[td.month - 1] + str(td.day)
outputName = 'model_' + today


### GRID SEARCH OVER ONE DISK HOLDING OTHER CONSTANT ###
def gridSearch(VariedDiskParams, StaticDiskParams, DI, num_iters):
	"""
	Takes: 		VariedDiskParams: list of lists
		   		StaticDiskParams: list of floats! Not searching over lists for the static one
				DI: Disk Index of varied disk (0 or 1). If 0, A is the varied disk and vice versa
	Returns: 	[X2 min value, Coordinates of X2 min]
	Creates:	Best fit two-disk model
	"""
	# Disk names should be the same as the output from makeModel()?

	# Pull the params we're looping over
	Tatms = VariedDiskParams[0]
	Tqq = VariedDiskParams[1]
	Xmol = VariedDiskParams[2]
	RAout = VariedDiskParams[3]
	PA = VariedDiskParams[4]
	Incl = VariedDiskParams[5]

	if DI == 0:
		outNameVaried = 'model-FittedA'
		outNameStatic = 'model-DiskB'
		DIs = 1
	else:
		outNameVaried = 'model-FittedB'
		outNameStatic = 'model-DiskA'
		DIs = 0

	makeModel(StaticDiskParams, outNameStatic, DIs)



	# Calculate the number of iterations this run will take (iterating over both disks)
	# num_iters = len(Tatms)*len(Tqq)*len(Xmol)*len(RAout)*len(PA)*len(Incl)
	# Set up a counter for the print out
	counter = 1

	# File I/O management: Create the full data (long) file
	f = open( outputName + '-long.log', 'w')
	f.write('ReducedChiSquared, RawChiSquared, TatmsA, TqqA, XmolA,	RAoutA,	PAA, InclA, TatmsB, TqqB, XmolB, RAoutB, PAB, InclB\n')
	f.close()
	# The params to be logged for the static disk (declaring them here clears things up at the pit of the for loop)
	outstrStatic = str(StaticDiskParams[0]) + ", " + str(StaticDiskParams[1]) + ", " + str(StaticDiskParams[2]) + ", " + str(StaticDiskParams[3]) + ", " + str(StaticDiskParams[4]) + ", " + str(StaticDiskParams[5])

	# Set up huge initial chi squared values so that later they will be improved upon.
	minRedX2 = 10000000000
	minRawX2 = 10000000000
	minX2Vals = [0,0,0,0,0,0]

	### GRIDLIFE ###
	for i in range(0,len(Tatms)):
		for j in range(0,len(Tqq)):
			for l in range(0,len(RAout)):
				for k in range(0,len(Xmol)):
					for m in range(0,len(PA)):
						for n in range(0,len(Incl)):
							# Create a list of floats to feed makeModel()
							ta = Tatms[i]
							tqq = Tqq[j]
							xmol = Xmol[k]
							raout = RAout[l]
							pa = PA[m]
							incl = Incl[n]
							params = [ta, tqq, xmol, raout, pa, incl]

							### Tell us where we are ###
							print "\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
							print "Currently fitting for: ", outNameVaried
							print "Beginning model ", str(counter)+"/"+str(num_iters)
							print "ta:", ta, "tqq", tqq, "xmol:", xmol, "raout:", raout, "pa:", pa, "incl:", incl
							print "Static params: ", StaticDiskParams

							### The model making/data management ###
							makeModel(params, outNameVaried, DI)
							sumDisks(outNameVaried, outNameStatic, outputName)


							# Careful to put these in the right spot!
							rawX2 = chiSq(outputName)[0]
							redX2 = chiSq(outputName)[1]

							# It's ok to split these up by disk since disk B's optimized params
							# will be independent of where disk A is.
							if DI == 0:
								diskARawX2[i, j, k, l, m, n] = rawX2
								diskARedX2[i, j, k, l, m, n] = redX2
							else:
								diskBRawX2[i, j, k, l, m, n] = chiSq(outputName)[0]
								diskBRedX2[i, j, k, l, m, n] = chiSq(outputName)[1]

							counter += 1


							### FILE UPDATING ###
							# Open the log file for writing (a for append)
							f = open(outputName + '-long.log', 'a')

							# Create the new line for the log file
							# If A is varied, we want varied to be printed into file first
							if DI == 0:
								outstr = str(redX2) + " " + str(rawX2) + " " + str(ta) + " " + str(tqq) + " " + str(xmol) + " " + str(raout) + " " + str(pa) + " " + str(incl) + " " + outstrStatic + '\n'
							else:
								outstr = outstrStatic + " " + str(diskBRedX2) + " " + str(diskBRawX2) + " " + str(ta) + " " + str(tqq) + " " + str(xmol) + " " + str(raout) + " " + str(pa) + " " + str(incl) + '\n'
							f.write(outstr)
							f.close()

							### PRINTOUT some info
							print
							print
							print "Raw Chi-Squared value:	 ", rawX2
							print "Reduced Chi-Squared value:", redX2

							# A counter to keep track of whether this is the best fit yet or not. Used to choose whether or not to delete this model so that we can always have a current-best-fit model.
							bestYet = 0
							if redX2 > 0 and redX2 < minRedX2:
								minRedX2 = redX2
								minX2Vals = [ta, tqq, xmol, raout, pa, incl]
								minX2Location = [i,j,k,l,m,n]
								bestYet = 1

							print "Min. Chi-Squared value so far:", minRedX2
							print "which happened at"
							print "ta:", minX2Vals[0], "tqq", minX2Vals[1], "xmol:", minX2Vals[2], "raout:", minX2Vals[3], "pa:", minX2Vals[4], "incl:", minX2Vals[5]

							# If this is the best fit so far, just change the model's name so that we can hold onto it.
							if bestYet == 1:
								sp.call('mv {}.fits model_{}-bestFit.fits'.format(outputName, today), shell=True)
								print "Best fit happened; moved files"
							# Now clear out all the files (im, vis, uvf, fits) made by chiSq()
							sp.call('rm -rf {}.*'.format(outputName), shell=True)





	# Find where the good stuff is at:
	#bestFitParams = [ Tatms[minX2Vals[0]], Tqq[minX2Vals[1]], Xmol[minX2Vals[2]], RAout[minX2Vals[3]], PA[minX2Vals[4]], Incl[minX2Vals[5]] ]
	#bestFitParams = [minX2Vals[0], minX2Vals[1], minX2Vals[2], minX2Vals[3], minX2Vals[4], minX2Vals[5] ]


	# Finally, make the best-fit model for this disk
	makeModel(minX2Vals, outNameVaried, DI)
	# No need to do a sumDisks() since we've only got one good disk so far


	print "Best-fit model created: ", outputName
	# Return the min value and where that value is
	print [minRedX2, minX2Vals]
	return [minRedX2, minX2Vals]







### PERFORM A FULL RUN USING FUNCTIONS ABOVE ###
def fullRun(diskAParams, diskBParams):
	# diskXParams are fed in from full_run.py where the parameter selections are made.

	# Calculate the number of steps and consequent runtime
	na = 1
	for a in range(0, len(diskAParams)):
		na *= len(diskAParams[a])
	nb = 1
	for b in range(0, len(diskBParams)):
		nb *= len(diskBParams[b])
	n = na + nb
	dt = 1.5							# minutes (time per iteration, approximately)
	t = dt * n / 60							# hours


	# Parameter Check:
	print "BEFORE STARTING A BIG RUN: Do a short test run and make sure the log file export works\n"
	print "This run will be iteratating through these parameters for Disk A:"
	print diskAParams
	print
	print "And these values for Disk B:"
	print diskBParams
	print
	print "This run will take ", n, "steps, spanning about ", t, "hours in the file", outputName
	print
	response = raw_input("Sound good? (press Enter to continue, any other key to stop)")
	if response != "":	#\n
		print "\nGo fix whatever you don't like and try again.\n\n"
		return
	else:
		print "Sounds good! Starting run.\n\n"




	### STARTING THE RUN ###

	# Start by fitting A and holding B constant

	# Make the initial static model (B), just with the first parameter values available
	dBInit = []
	for i in diskBParams:
		dBInit.append(i[0])


	# Grid search, then save those indices that gridSearch() returns as newStatic. DI = 0 because we're choosing to vary A first.
	fitAParams = gridSearch(diskAParams, dBInit, 0, n)[1]
	print "First disk has been fit\n"

	# Now search over the other disk
	fitBParams = gridSearch(diskBParams, fitAParams, 1, n)[1]

	# Names:
	diskAName, diskBName = 'fitA', 'fitB'
	# Create the best-fit model
	makeModel(fitAParams, diskAName, 0)
	makeModel(fitBParams, diskBName, 1)
	sumDisks(diskAName, diskBName, outputName)
	print "Best-fit model created: ", outputName, ".fits"


	# Calculate and present the final X2 values. Note that here, outputName is just the infile for chiSq()
	finalX2s = chiSq(outputName)
	print "Final Raw Chi-Squared Value: ", finalX2s[0]
	print "Final Reduced Chi-Squared Value: ", finalX2s[1]


	#A short log file with best fit vals, range queried, indices of best vals, best chi-squared.
	# Finally, write out the short file:
	# 	- (maybe figure out how to round these for better readability)
	f = open( outputName + '-short.log', 'w')
	s1 = '\nBest Chi-Squared values [raw, reduced]:' + str(finalX2s)
	f.write(s1)
	s2 = '\n\n\nParameter ranges queried:\n' + '\nDisk A:' + str(diskAParams) + '\n\nDisk B:' + str(diskBParams)
	f.write(s2)
	s3 = '\n\n\nBest-fit values (Tatm, Tqq, Xmol, outerR, PA, Incl):' + '\nDisk A:' + str(fitAParams) + '\nDisk B:' + str(fitBParams)
	f.write(s3)
	f.close()


	"""
	# Export a table of the best fit values, the values queries, and the final chi-squared values.
	# Note that, in order to keep the table's form, the chi-squared vals (raw and reduced) are stacked.
	s1 = 'X2s_final, Tatms_final, Tatms_tried, Tqq_final, Tqq_tried, Xmol_final, Xmol_tried, , Rout_final, Rout_tried, Incl_final, Incl_tried\n'
	s2 = finalX2s[0], fitAParams[0], diskAParams[0], fitAParams[1], diskAParams[1], fitAParams[2], diskAParams[2], fitAParams[3], diskAParams[3], fitAParams[5], diskAParams[5]
	s3 = finalX2s[1], fitBParams[0], diskBParams[0], fitBParams[1], diskBParams[1], fitBParams[2], diskBParams[2], fitBParams[3], diskBParams[3], fitBParams[5], diskBParams[5]

	f = open( outputName + '-short.log', 'w')
	f.write(s1)
	f.write(s2)
	f.write(s3)
	f.close()
	"""





# The End
