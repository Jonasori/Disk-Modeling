"""Run a grid search."""


import datetime
import numpy as np
import subprocess as sp
import pandas as pd
import cPickle as pickle
from tools import icr
from utils import makeModel, sumDisks, chiSq
from run_params import diskAParams, diskBParams


# Name the output file
td = datetime.datetime.now()
months = ['jan', 'feb', 'march', 'april', 'may',
          'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']
today = months[td.month - 1] + str(td.day)

# Not sure this is set up right yet.
sp.call(['mkdir', 'models/run_{}'.format(today)])
sp.call(['mkdir', '/scratch/jonas/run_{}'.format(today)])
run_dir = './models/run_' + today
scratch_dir = '/scratch/jonas/run_' + today
sp.call(['ln -s {} {}'.format(scratch_dir, run_dir)])

# outputName = 'model_' + today  # + 'df_out_test'
outputPath = 'models/run_' + today + '/'

# A little silly, but an easy way to name disks by their disk index (DI)
dnames = ['A', 'B']

# Prep some storage space for all the chisq vals
diskARawX2 = np.zeros((len(diskAParams[0]), len(diskAParams[1]),
                       len(diskAParams[2]), len(diskAParams[3]),
                       len(diskAParams[4]), len(diskAParams[5])))

diskBRawX2 = np.zeros((len(diskBParams[0]), len(diskBParams[1]),
                       len(diskBParams[2]), len(diskBParams[3]),
                       len(diskBParams[4]), len(diskBParams[5])))

diskARedX2 = np.zeros((len(diskAParams[0]), len(diskAParams[1]),
                       len(diskAParams[2]), len(diskAParams[3]),
                       len(diskAParams[4]), len(diskAParams[5])))

diskBRedX2 = np.zeros((len(diskAParams[0]), len(diskBParams[1]),
                       len(diskBParams[2]), len(diskBParams[3]),
                       len(diskBParams[4]), len(diskBParams[5])))


# GRID SEARCH OVER ONE DISK HOLDING OTHER CONSTANT
def gridSearch(VariedDiskParams, StaticDiskParams, DI, num_iters, steps_so_far=1):
    """
    Run a grid search over parameter space.

    Args:
        VariedDiskParams (list of lists): lists of param vals to try.
        StaticDiskParams (list of floats) Single vals for the static model.
        DI: Disk Index of varied disk (0 or 1).
            If 0, A is the varied disk and vice versa
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

    # Get the index of the static disk, name the outputs
    DIs = abs(DI - 1)
    outNameVaried = outputPath + 'fitted_' + dnames[DI]
    outNameStatic = outputPath + 'static_' + dnames[DIs]

    makeModel(StaticDiskParams, outNameStatic, DIs)

    counter = steps_so_far

    # Set up huge initial chi squared values so that they can be improved upon.
    minRedX2 = 10000000000
    minRawX2 = 10000000000
    minX2Vals = [0, 0, 0, 0, 0, 0]

    # GRIDLIFE #
    for i in range(0, len(Tatms)):
        for j in range(0, len(Tqq)):
            for l in range(0, len(RAout)):
                for k in range(0, len(Xmol)):
                    for m in range(0, len(PA)):
                        for n in range(0, len(Incl)):
                            # Create a list of floats to feed makeModel()
                            ta = Tatms[i]
                            tqq = Tqq[j]
                            xmol = Xmol[k]
                            raout = RAout[l]
                            pa = PA[m]
                            incl = Incl[n]
                            params = [ta, tqq, xmol, raout, pa, incl]

                            print "\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                            print "Currently fitting for: ", outNameVaried
                            print "Beginning model ", str(
                                counter)+"/"+str(num_iters)
                            print "ta:", ta
                            print "tqq", tqq
                            print "xmol:", xmol
                            print "raout:", raout
                            print "pa:", pa
                            print "incl:", incl
                            print "Static params: ", StaticDiskParams

                            # The model making/data management
                            makeModel(params, outNameVaried, DI)
                            sumDisks(outNameVaried, outNameStatic, outputPath)

                            # Careful to put these in the right spot!
                            X2s = chiSq(outputPath)
                            rawX2, redX2 = X2s[0], X2s[1]

                            # It's ok to split these up by disk since disk B's
                            # best params are independent of where disk A is.
                            if DI == 0:
                                diskARawX2[i, j, k, l, m, n] = rawX2
                                diskARedX2[i, j, k, l, m, n] = redX2
                            else:
                                diskBRawX2[i, j, k, l, m, n] = rawX2
                                diskBRedX2[i, j, k, l, m, n] = redX2

                            counter += 1

                            print "\n\n"
                            print "Raw Chi-Squared value:	 ", rawX2
                            print "Reduced Chi-Squared value:", redX2

                            df_row = {
                                'Atms Temp': ta,
                                'Temp Struct': tqq,
                                'Molecular Abundance': xmol,
                                'Outer Radius': raout,
                                'Pos. Angle': pa,
                                'Incl.': incl,
                                'Raw Chi2': rawX2,
                                'Reduced Chi2': redX2
                                }
                            df_rows.append(df_row)

                            # A counter to keep track of whether this is the
                            # best fit yet or not. Used to choose whether or
                            # not to delete this model so that we can always
                            # have a current-best-fit model.
                            bestYet = 0
                            if redX2 > 0 and redX2 < minRedX2:
                                minRedX2 = redX2
                                minX2Vals = [ta, tqq, xmol, raout, pa, incl]
                                minX2Location = [i, j, k, l, m, n]
                                bestYet = 1

                            print "Min. Chi-Squared value so far:", minRedX2
                            print "which happened at: "
                            print "ta:", minX2Vals[0]
                            print "tqq", minX2Vals[1]
                            print "xmol:", minX2Vals[2]
                            print "raout:", minX2Vals[3]
                            print "pa:", minX2Vals[4]
                            print "incl:", minX2Vals[5]

                            # If this is the best fit so far, just change the model's name so that we can hold onto it.
                            if bestYet == 1:
                                sp.call(
                                    'mv {}.fits model_{}-bestFit.fits'.format(outputPath, today), shell=True)
                                print "Best fit happened; moved files"
                            # Now clear out all the files (im, vis, uvf, fits) made by chiSq()
                            sp.call('rm -rf {}.*'.format(outputPath), shell=True)

    # Finally, make the best-fit model for this disk
    makeModel(minX2Vals, outNameVaried, DI)
    print "Best-fit model created: ", outputPath

    # Knit the dataframe
    step_log = pd.DataFrame(df_rows)
    print "Shape of long-log data frame is ", step_log.shape

    # Return the min value and where that value is
    print "Minimum Chi2 value and where it happened: ", [minRedX2, minX2Vals]
    return step_log


# PERFORM A FULL RUN USING FUNCTIONS ABOVE #
def fullRun(diskAParams, diskBParams):
    """Run it all.

    diskXParams are fed in from full_run.py,
    where the parameter selections are made.
    """
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
    print "This run will be iteratating through these parameters for Disk A:"
    print diskAParams
    print "\nAnd these values for Disk B:\n", diskBParams
    print "\nThis run will take ", n, "steps, spanning about ", t, "hours in the file", outputPath, '\n'
    response = raw_input(
        "Sound good? (press Enter to continue, any other key to stop)")
    if response != "":
        print "\nGo fix whatever you don't like and try again.\n\n"
        return
    else:
        print "Sounds good! Starting run.\n\n"

    # STARTING THE RUN #
    # Make the initial static model (B), just with the first parameter values
    dBInit = []
    for i in diskBParams:
        dBInit.append(i[0])

    # Grid search over Disk A, retrieve the resulting pd.DataFrame
    df_A_fit = gridSearch(diskAParams, dBInit, 0, n)

    # Find where the chi2 is minimized and save it
    idx_of_BF_A = df_A_fit.index[df_A_fit['Reduced Chi2'] == np.min(
        df_A_fit['Reduced Chi2'])][0]
    print "Index of Best Fit, A is ", idx_of_BF_A

    # Make a list of those parameters to pass the next round of grid searching.
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

    idx_of_BF_B = df_B_fit.index[df_B_fit['Reduced Chi2'] == np.min(
        df_B_fit['Reduced Chi2'])][0]

    Ps_B = [df_B_fit['Atms Temp'][idx_of_BF_B],
            df_B_fit['Temp Struct'][idx_of_BF_B],
            df_B_fit['Molecular Abundance'][idx_of_BF_B],
            df_B_fit['Outer Radius'][idx_of_BF_B],
            df_B_fit['Pos. Angle'][idx_of_BF_B],
            df_B_fit['Incl.'][idx_of_BF_B]]
    fit_B_params = np.array(Ps_B)

    # Create the final best-fit model.
    # Final model names:
    diskAName, diskBName = outputPath + 'fitA', outputPath + 'fitB'

    makeModel(fit_A_params, outputPath + 'fitA', 0)
    makeModel(fit_B_params, diskBName, 1)
    sumDisks(diskAName, diskBName, outputPath)

    # Bind the data frames, output them.
    # This is reiterated in tools.py/depickler(), but we can unwrap these vals with:
    # full_log.loc['A', :] to get all the columns for disk A, or full_log[:, 'Incl.'] to see which inclinations both disks tried.
    full_log = pd.concat([df_A_fit, df_B_fit], keys=['A', 'B'], names=['Disk'])
    # Pickle the step log df.
    pickle.dump(full_log, open('{}_step-log.pickle'.format(outputPath), "wb"))
    # To read the pickle:
    # f = pickle.load(open('{}_step-log.pickle'.format(outputPath), "rb"))

    # Alternatively, to get a csv:
    # full_log.to_csv(path_or_buf='{}_step-log.csv'.format(outputPath))

    # Convolve the final model
    icr(outputPath, mol=mol)
    print "Best-fit model created: ", outputPath, ".cm"

    # Calculate and present the final X2 values. Note that here, outputPath is just the infile for chiSq()
    finalX2s = chiSq(outputPath)
    print "Final Raw Chi-Squared Value: ", finalX2s[0]
    print "Final Reduced Chi-Squared Value: ", finalX2s[1]

    # A short log file with best fit vals, range queried, indices of best vals, best chi-squared.
    # Finally, write out the short file:
    # 	- (maybe figure out how to round these for better readability)
    f = open(outputPath + '-short.log', 'w')
    s1 = '\nBest Chi-Squared values [raw, reduced]:' + str(finalX2s)
    f.write(s1)
    s2 = '\n\n\nParameter ranges queried:\n' + '\nDisk A:\n' + \
        str(diskAParams) + '\n\nDisk B:\n' + str(diskBParams)
    f.write(s2)
    s3 = '\n\n\nBest-fit values (Tatm, Tqq, Xmol, outerR, PA, Incl):' + \
        '\nDisk A:\n' + str(fit_A_params) + '\nDisk B:\n' + str(fit_B_params)
    f.write(s3)
    f.close()


# The End
