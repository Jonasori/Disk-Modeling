"""Run a grid search."""


import numpy as np
import subprocess as sp
import pandas as pd
import cPickle as pickle
import time
import csv

# Local package files
from utils import makeModel, sumDisks, chiSq
from run_params import diskAParams, diskBParams
from constants import mol, today, dataPath
from tools import icr, sample_model_in_uvplane, remove
from analysis import plot_gridSearch_log, plot_step_duration


# Hopefully no more than 1 runs/day!
# This doesn't work bc full_run already wipes out old directories.
# Fix this some time.

modelPath = './models/run_' + today + '/' + today
"""
if already_exists(modelPath):
    modelPath = './models/run_' + today + '_2/' + today + '_2'
    print "One run has already happened today; running in", modelPath
"""
# A little silly, but an easy way to name disks by their disk index (DI)
dnames = ['A', 'B']
# Set up a list to keep track of how long each iteration takes.
times = [['step', 'duration']]

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
def gridSearch(VariedDiskParams, StaticDiskParams, DI,
               num_iters, steps_so_far=1):
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
    R_out = VariedDiskParams[3]
    PA = VariedDiskParams[4]
    Incl = VariedDiskParams[5]

    # Initiate a list to hold the rows of the df
    df_rows = []

    # Get the index of the static disk, name the outputs
    DIs = abs(DI - 1)
    outNameVaried = modelPath + 'fitted_' + dnames[DI]
    outNameStatic = modelPath + 'static_' + dnames[DIs]

    makeModel(StaticDiskParams, outNameStatic, DIs)

    # Set up huge initial chi squared values so that they can be improved upon.
    minRedX2 = 10000000000
    minX2Vals = [0, 0, 0, 0, 0, 0]

    counter = steps_so_far

    # GRIDLIFE
    for i in range(0, len(Tatms)):
        for j in range(0, len(Tqq)):
            for l in range(0, len(R_out)):
                for k in range(0, len(Xmol)):
                    for m in range(0, len(PA)):
                        for n in range(0, len(Incl)):
                            # Create a list of floats to feed makeModel()
                            begin = time.time()
                            ta = Tatms[i]
                            tqq = Tqq[j]
                            xmol = Xmol[k]
                            r_out = R_out[l]
                            pa = PA[m]
                            incl = Incl[n]
                            params = [ta, tqq, xmol, r_out, pa, incl]

                            print "\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                            print "Currently fitting for: ", outNameVaried
                            print "Beginning model ", str(
                                counter + steps_so_far) + "/"+str(num_iters)
                            print "ta:", ta
                            print "tqq", tqq
                            print "xmol:", xmol
                            print "r_out:", r_out
                            print "pa:", pa
                            print "incl:", incl
                            print "Static params: ", StaticDiskParams

                            # Make a new disk, sum them, sample in vis-space.
                            makeModel(params, outNameVaried, DI)
                            sumDisks(outNameVaried, outNameStatic, modelPath)
                            sample_model_in_uvplane(modelPath, dataPath, mol=mol)

                            # Visibility-domain chi-squared evaluation
                            rawX2, redX2 = chiSq(modelPath)

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

                            df_row = {'Atms Temp': ta,
                                      'Temp Struct': tqq,
                                      'Molecular Abundance': xmol,
                                      'Outer Radius': r_out,
                                      'Pos. Angle': pa,
                                      'Incl.': incl,
                                      'Raw Chi2': rawX2,
                                      'Reduced Chi2': redX2
                                      }
                            df_rows.append(df_row)
                            # Maybe want to re-export the df every time here?

                            if redX2 > 0 and redX2 < minRedX2:
                                minRedX2 = redX2
                                minX2Vals = [ta, tqq, xmol, r_out, pa, incl]
                                # minX2Location = [i, j, k, l, m, n]
                                sp.call(
                                    'mv {}.fits {}_bestFit.fits'.format(modelPath, modelPath), shell=True)
                                print "Best fit happened; moved file"

                            # Now clear out all the files (im, vis, uvf, fits)
                            remove(modelPath + ".*")
                            # sp.call('rm -rf {}.*'.format(modelPath),
                            #         shell=True)

                            print "Min. Chi-Squared value so far:", minRedX2
                            print "which happened at: "
                            print "ta:", minX2Vals[0]
                            print "tqq:", minX2Vals[1]
                            print "xmol:", minX2Vals[2]
                            print "r_out:", minX2Vals[3]
                            print "pa:", minX2Vals[4]
                            print "incl:", minX2Vals[5]

                            finish = time.time()
                            times.append([counter, finish - begin])

    # Finally, make the best-fit model for this disk
    makeModel(minX2Vals, outNameVaried, DI)
    print "Best-fit model for disk", dnames[DI], " created: ", modelPath, ".fits\n\n"

    # Knit the dataframe
    step_log = pd.DataFrame(df_rows)
    print "Shape of long-log data frame is ", step_log.shape

    # Return the min value and where that value is
    print "Minimum Chi2 value and where it happened: ", [minRedX2, minX2Vals]
    return step_log


# PERFORM A FULL RUN USING FUNCTIONS ABOVE #
def fullRun(diskAParams, diskBParams, use_a_previous_result=False):
    """Run it all.

    diskXParams are fed in from full_run.py,
    where the parameter selections are made.
    """
    t0 = time.time()

    # Calculate the number of steps and consequent runtime
    na = 1
    for a in range(0, len(diskAParams)):
        na *= len(diskAParams[a])

    nb = 1
    for b in range(0, len(diskBParams)):
        nb *= len(diskBParams[b])

    n, dt = na + nb, 2.5
    t = n * dt
    if t < 60:
        t = str(n * dt) + " minutes."
    else:
        t = str(n * dt/60) + " hours."

    # Parameter Check:
    print "This run will be iteratating through these parameters for Disk A:"
    print diskAParams
    print "\nAnd these values for Disk B:\n", diskBParams
    print "\nThis run will take", n, "steps, spanning about ", t
    print "\nOutput will be in", modelPath, '\n'
    response = raw_input(
        "Sound good? (press Enter to continue, any other key to stop)")
    if response != "":
        print "\nGo fix whatever you don't like and try again.\n\n"
        return
    else:
        print "Sounds good!n\n"

    if use_a_previous_result is True:
        response2 = raw_input(
            'Please enter the path to the .fits file to use from a previous',
            'run (should be ./models/date/run_date/datefitted_[A or B].fits)\n'
        )
        if 'A' in response2:
            to_skip = 'A'
        elif 'B' in response2:
            to_skip = 'B'
        else:
            print "Bad path; must have 'fitted_A or fitted_B' in it. Try again"
            return
    # STARTING THE RUN #
    # Make the initial static model (B), just with the first parameter values
    dBInit = []
    for i in diskBParams:
        dBInit.append(i[0])

    # Grid search over Disk A, retrieve the resulting pd.DataFrame
    if to_skip != 'A':
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

    # Bind the data frames, output them.
    # Reiterated in tools.py/depickler(), but we can unwrap these vals with:
    # full_log.loc['A', :] to get all the columns for disk A, or
    # full_log[:, 'Incl.'] to see which inclinations both disks tried.
    full_log = pd.concat([df_A_fit, df_B_fit], keys=['A', 'B'], names=['Disk'])
    # Pickle the step log df.
    pickle.dump(full_log, open('{}_step-log.pickle'.format(modelPath), "wb"))
    # To read the pickle:
    # f = pickle.load(open('{}_step-log.pickle'.format(modelPath), "rb"))
    # Alternatively, to get a csv:
    # full_log.to_csv(path_or_buf='{}_step-log.csv'.format(modelPath))

    # Finally, Create the final best-fit model.
    print "\n\nCreating best fit model now"
    sample_model_in_uvplane(modelPath + '_bestFit', dataPath, mol=mol)
    icr(modelPath + '_bestFit', mol=mol)
    print "Best-fit model created: " + modelPath + "_bestFit.im\n\n"

    # Calculate and present the final X2 values.
    finalX2s = chiSq(modelPath + '_bestFit')
    print "Final Raw Chi-Squared Value: ", finalX2s[0]
    print "Final Reduced Chi-Squared Value: ", finalX2s[1]

    # Clock out
    t1 = time.time()
    t_total = (t1 - t0)/60
    # n+4 to account for best-fit model making and static disks in grid search
    t_per = str(t_total/(n + 4))

    with open(modelPath + '_stepDurations.csv', 'w') as f:
        wr = csv.writer(f)
        wr.writerows(times)

    print "\n\nFinal run duration was", t_total/60, ' hours'
    print 'with each step taking on average', t_per, ' minutes'

    # log file w/ best fit vals, range queried, indices of best vals, best chi2
    # 	- (maybe figure out how to round these for better readability)
    param_names = ['ta', 'tqq', 'xmol', 'r_out', 'pa', 'incl']
    with open('run_' + today + 'summary.log', 'w') as f:
        s0 = '\nLOG FOR RUN ON' + today + ' FOR THE ' + mol + ' LINE'
        s1 = '\nBest Chi-Squared values [raw, reduced]:\n' + str(finalX2s)

        s2 = '\n\n\nParameter ranges queried:\n'
        s3 = '\nDisk A:\n'
        for i, ps in enumerate(diskAParams):
            s3 = s3 + param_names[i] + str(ps) + '\n'
        s4 = '\nDisk B:\n'
        for i, ps in enumerate(diskBParams):
            s4 = s4 + param_names[i] + str(ps) + '\n'

        s5 = '\n\n\nBest-fit values (Tatm, Tqq, Xmol, outerR, PA, Incl):'
        s6 = '\nDisk A:\n' + str(fit_A_params)
        s7 = '\nDisk B:\n' + str(fit_B_params)

        s8 = '\n\n\nFinal run duration was' + str(t_total/60) + 'hours'
        s9 = '\nwith each step taking on average' + t_per + 'minutes'

        s = s0 + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9
        f.write(s)

    plot_gridSearch_log(modelPath, show=False)
    plot_step_duration(modelPath, show=False)

# The End
