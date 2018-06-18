
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
from tools import icr
import pandas as pd
import cPickle as pickle
from numba import jit


# Velocity axes might be backwards
# options=3value csize=1,2
# Write into short log file how many steps were taken


# Name the output file
td = datetime.datetime.now()
months = ['jan', 'feb', 'march', 'april', 'may', 'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']
today = months[td.month - 1] + str(td.day)
outputName = 'model_' + today	# + 'df_out_test'


# Data file name:
data_file = 'data-hco'



# Prep some storage space for all the chisq vals

diskARawX2 = np.zeros((len(diskAParams[0]), len(diskAParams[1]), len(diskAParams[2]), len(diskAParams[3]), len(diskAParams[4]), len(diskAParams[5])))
diskBRawX2 = np.zeros((len(diskBParams[0]), len(diskBParams[1]), len(diskBParams[2]), len(diskBParams[3]), len(diskBParams[4]), len(diskBParams[5])))

diskARedX2 = np.zeros((len(diskAParams[0]), len(diskAParams[1]), len(diskAParams[2]), len(diskAParams[3]), len(diskAParams[4]), len(diskAParams[5])))
diskBRedX2 = np.zeros((len(diskAParams[0]), len(diskBParams[1]), len(diskBParams[2]), len(diskBParams[3]), len(diskBParams[4]), len(diskBParams[5])))


### GRID SEARCH OVER ONE DISK HOLDING OTHER CONSTANT ###
def gridSearch(VariedDiskParams, StaticDiskParams, DI, num_iters, steps_so_far=0):
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
	
	# Initiate a list to hold the rows of the df
	df_rows = []

	# Get the correct name for the output
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
	counter = steps_so_far
	# if DI==1:
	#	counter += num_steps(disk A)


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
							# Make this print na + counter when fitting B
							print "\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
							print "Currently fitting for: ", outNameVaried
							print "Beginning model ", str(counter)+"/"+str(num_iters)
							print "ta:", ta, "tqq", tqq, "xmol:", xmol, "raout:", raout, "pa:", pa, "incl:", incl
							print "Static params: ", StaticDiskParams

							### The model making/data management ###
							makeModel(params, outNameVaried, DI)
							sumDisks(outNameVaried, outNameStatic, outputName)


							# Careful to put these in the right spot!
							X2s = chiSq(outputName)
							rawX2, redX2 = X2s[0], X2s[1]

							# It's ok to split these up by disk since disk B's optimized params
							# will be independent of where disk A is.
							if DI == 0:
								diskARawX2[i, j, k, l, m, n] = rawX2
								diskARedX2[i, j, k, l, m, n] = redX2
							else:
								diskBRawX2[i, j, k, l, m, n] = rawX2
								diskBRedX2[i, j, k, l, m, n] = redX2

							counter += 1


							### PRINTOUT some info
							print "\n\n"
							print "Raw Chi-Squared value:	 ", rawX2
							print "Reduced Chi-Squared value:", redX2
							
							# Add this step to the step df
							df_row = {
                                                                'Atms Temp':ta,
                                                                'Temp Struct':tqq,
                                                                'Molecular Abundance':xmol,
                                                                'Outer Radius':raout,
                                                                'Pos. Angle':pa,
                                                                'Incl.':incl,
								'Raw Chi2':rawX2,
								'Reduced Chi2':redX2
                                                                }
							df_rows.append(df_row)


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




	# Finally, make the best-fit model for this disk
	makeModel(minX2Vals, outNameVaried, DI)
	print "Best-fit model created: ", outputName
	
	# Knit the dataframe
	step_log = pd.DataFrame(df_rows)
	print "Shape of long-log data frame is ", step_log.shape


	# Return the min value and where that value is
	print "Minimum Chi2 value and where it happened: ", [minRedX2, minX2Vals]
	return step_log







### PERFORM A FULL RUN USING FUNCTIONS ABOVE ###
def fullRun(diskAParams, diskBParams):
	# diskXParams are fed in from full_run.py where the parameter selections are made.

	# Calculate the number of steps and consequent runtime
	na = 1
	for a in range(0, len(diskAParams)):
		na *= len(diskAParams[a])

	nb = 1
	for b in range(0, len(diskBParams)):
		nb *= len(diskAParams[b])

	n = na + nb
	dt = 1.5							# minutes (time per iteration, approximately)
	t = dt * n / 60							# hours


	# Parameter Check:
	print "BEFORE STARTING A BIG RUN: Do a short test run and make sure the log file export works\n"
	print "This run will be iteratating through these parameters for Disk A:"
	print diskAParams
	print "\nAnd these values for Disk B:"
	print diskBParams
	print "\nThis run will take ", n, "steps, spanning about ", t, "hours in the file", outputName, '\n'
	response = raw_input("Sound good? (press Enter to continue, any other key to stop)")
	if response != "":
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



	df_A_fit = gridSearch(diskAParams, dBInit, 0, n)	# Grid search over Disk A, retrieve the resulting pd.DataFrame
	df_A_fit.assign(Disk_Name = 'A')			# Add a column to tell which disk this is

	print "Shape of df_A_fit is ", df_A_fit.shape

	# Find where the chi2 is minimized and save it
	idx_of_BF_A = df_A_fit.index[df_A_fit['Reduced Chi2'] == np.min(df_A_fit['Reduced Chi2'])][0]
	print "Index of Best Fit, A is ", idx_of_BF_A
	
	# Make a list of those parameters to pass to the next round of grid searching.
	Ps_A = [df_A_fit['Atms Temp'][idx_of_BF_A], 
		df_A_fit['Temp Struct'][idx_of_BF_A],
		df_A_fit['Molecular Abundance'][idx_of_BF_A],
		df_A_fit['Outer Radius'][idx_of_BF_A],
		df_A_fit['Pos. Angle'][idx_of_BF_A],
		df_A_fit['Incl.'][idx_of_BF_A]]
	fit_A_params = np.array(Ps_A)


	print "First disk has been fit\n"


	# Now search over the other disk
	df_B_fit = gridSearch(diskBParams, fit_A_params, 1, n, steps_so_far=na)
	df_B_fit.assign(Disk_Name = 'B')
	idx_of_BF_B = df_B_fit.index[df_B_fit['Reduced Chi2'] == np.min(df_B_fit['Reduced Chi2'])][0]
	Ps_B = [df_B_fit['Atms Temp'][idx_of_BF_B],
                df_B_fit['Temp Struct'][idx_of_BF_B],
                df_B_fit['Molecular Abundance'][idx_of_BF_B],
                df_B_fit['Outer Radius'][idx_of_BF_B],
                df_B_fit['Pos. Angle'][idx_of_BF_B],
                df_B_fit['Incl.'][idx_of_BF_B]]
	fit_B_params = np.array(Ps_B)	


	# Create the final best-fit model.
	# Final model names:
	diskAName, diskBName = 'fitA', 'fitB'

	makeModel(fit_A_params, diskAName, 0)
	makeModel(fit_B_params, diskBName, 1)
	sumDisks(diskAName, diskBName, outputName)
	
	
	# Bind the data frames, output them.
        # This is reiterated in tools.py/depickler(), but we can unwrap these vals with:
	# full_log.loc['A', :] to get all the columns for disk A, or full_log[:, 'Incl.'] to see which inclinations both disks tried.
	full_log = pd.concat([df_A_fit, df_B_fit], keys=['A', 'B'], names=['Disk'])
	# Pickle the step log df.
	pickle.dump( full_log, open( '{}_step-log.pickle'.format(outputName), "wb" ) )
	# To read the pickle:
	# full_log = pickle.load( open( '{}_step-log.pickle'.format(outputName), "rb" ) )
	
	# Alternatively, to get a csv:
	#full_log.to_csv(path_or_buf='{}_step-log.csv'.format(outputName))



	# Convolve the final model
	icr(outputName)
	print "Best-fit model created: ", outputName, ".[fits/some other ones]"


	# Calculate and present the final X2 values. Note that here, outputName is just the infile for chiSq()
	finalX2s = chiSq(outputName)
	print "Final Raw Chi-Squared Value: ", finalX2s[0] 
	print "Final Reduced Chi-Squared Value: ", finalX2s[1]




	# A short log file with best fit vals, range queried, indices of best vals, best chi-squared.
	# Finally, write out the short file:
	# 	- (maybe figure out how to round these for better readability)
	f = open( outputName + '-short.log', 'w')
	s1 = '\nBest Chi-Squared values [raw, reduced]:' + str(finalX2s)
	f.write(s1)
	s2 = '\n\n\nParameter ranges queried:\n' + '\nDisk A:\n' + str(diskAParams) + '\n\nDisk B:\n' + str(diskBParams)
	f.write(s2)
	s3 = '\n\n\nBest-fit values (Tatm, Tqq, Xmol, outerR, PA, Incl):' + '\nDisk A:\n' + str(fit_A_params) + '\nDisk B:\n' + str(fit_B_params)
	f.write(s3)
	f.close()





# The End
