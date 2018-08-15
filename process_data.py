"""Data processing pipeline.

A small change
To be run from /Volumes/disks/jonas/freshStart/modeling
sp.Popen vs sp.call: Popen lets you change working directory for the call with
                     cwd arg, call blocks further action until its action is
                     complete, although Popen can be made to block with .wait()
"""


import time
import argparse
import numpy as np
import subprocess as sp
from astropy.io import fits
from constants import lines, today
from var_vis import var_vis
from tools import icr, already_exists, pipe, remove


def casa_sequence(mol, raw_data_path, output_path,
                  cut_baselines=False, remake_all=False):
    """Cvel, split, and export as uvf the original cont-sub'ed .ms.

    Args:
        - mol:
        - raw_data_path:
        - output_path: path, with name included
        - spwID: the line's spectral window ID. spwID(HCO+) = 1
        - cut_baselines: obvious.
        - remake_all (bool): if True, remove delete all pre-existing files.
    """
    # blah
    split_range = find_split_cutoffs(mol)
    print "Split range is ", str(split_range[0]), str(split_range[1])

    # FIELD SPLIT
    # All files past this point should be saved to a different directory.
    remove(raw_data_path + '-' + mol + '.ms')
    pipe(["split(",
          "vis='{}calibrated.ms',".format(raw_data_path),
          "outputvis='{}calibrated-{}.ms',".format(raw_data_path, mol),
          "field='OrionField4',",
          "spw={})".format(lines[mol]['spwID'])])

    # CONTINUUM SUBTRACTION
    # Want to exlude the data disk from our contsub, so use split_range
    remove(raw_data_path + '-' + mol + '.ms.contsub')
    pipe(["uvcontsub(",
          "vis='{}calibrated-{}.ms',".format(raw_data_path, mol),
          "fitspw={},".format(split_range),
          "excludechans=True,",
          "spw='0'"])

    # CVEL
    remove(output_path + '_cvel.ms')
    # The values of width and start should be changed.
    pipe(["cvel(",
          "vis='{}calibrated-{}.ms.contsub',".format(raw_data_path, mol),
          "outputvis='{}_cvel.ms',".format(output_path),
          "field='',",
          "mode='velocity',",
          # "nchans=-1,",
          # "width={},".format(width),
          # "start={},".format(start),
          "restfreq='{}GHz',".format(lines[mol]['restfreq']),
          "outframe='LSRK')"
          ])

    remove(output_path + '_split.ms')
    # There is only one spw now, so this is ok to do.
    spw = '0:' + str(split_range[0]) + '~' + str(split_range[1])
    split_str = (["split(",
                  "vis='{}_cvel.ms',".format(output_path),
                  "outputvis='{}_split.ms',".format(output_path),
                  "spw='{}',".format(spw),
                  "datacolumn='all',",
                  "keepflags=False)"
                  ])

    # If necessary, insert a baseline cutoff. Not appending because we want
    # to keep the ) in the right spot, so just put uvrange= in the middle.
    if cut_baselines is True:
        print "\nCutting baselines in casa_sequence\n"
        b_min = lines[mol]['baseline_cutoff']
        split_str = split_str[:-2] + \
            [("uvrange='>" + str(b_min) + "klambda',")] + \
            split_str[-2:]

    pipe(split_str)

    # EXPORT IT
    remove(output_path + '_exportuvfits.uvf')
    pipe(["exportuvfits(",
          "vis='{}_split.ms',".format(output_path),
          "fitsfile='{}_exportuvfits.uvf')".format(output_path)
          ])


def find_split_cutoffs(mol, other_restfreq=0):
    """Find the indices of the 50 channels around the restfreq.

    chan_dir, chan0, nchans, chanstep from
    listobs(vis='raw_data/calibrated-mol.ms.contsub')
    """
    chan_dir = lines[mol]['chan_dir']
    chan0 = lines[mol]['chan0']
    restfreq = lines[mol]['restfreq']

    # ALl in GHz. Both values pulled from listobs
    nchans = 3840
    chanstep = 0.000488281 * chan_dir
    freqs = [chan0 + chanstep*i for i in range(nchans)]

    # Using these two different restfreqs yields locs of 1908 vs 1932. Weird.
    if other_restfreq != 0:
        restfreq = other_restfreq

    # Find the index of the restfreq channel
    loc = 0
    min_diff = 1
    for i in range(len(freqs)):
        diff = abs(freqs[i] - restfreq)
        if diff < min_diff:
            min_diff = diff
            loc = i

    # Need to account for the systemic velocitys shift of. Do so by rearranging
    # d_nu/nu = dv/c
    # ((sysv/c) * restfreq)/chanstep = nchans of shift to apply
    # = (10.55/3e5) * 356.734223/0.000488281 = 25.692
    # So shift in an extra 26 channels
    loc = loc - 26 if loc > 26 else -np.inf
    split_range = [loc - 25, loc + 25]

    # v_step = 0.410339      # km/s
    # split_range_vel =
    return split_range


def baseline_cutter(mol):
    """Cut a vis file.

    It seems like doing this with uvaver is no good because it drops the
    SPECSYS keyword from the header, so now implementing it with CASA in the
    split early on, so this is no longer used.

    This one uses Popen and cwd (change working directory) because the path was
    getting to be longer than buffer's 64-character limit. Could be translated
    to other funcs as well, but would just take some work.
    """
    filepath = './data/' + mol + '/'
    min_baseline = lines[mol]['baseline_cutoff']
    name = mol
    new_name = name + '-short' + str(min_baseline)

    print "\nCompleted uvaver; starting fits uvout\n"
    sp.call(['fits',
             'op=uvout',
             'in={}.vis'.format(new_name),
             'out={}.uvf'.format(new_name)],
            cwd=filepath)

    # Now clean that out file.
    print "\nCompleted fits uvout; starting ICR\n\n"
    icr(filepath + new_name, mol)

    # For some reason icr is returning and so it never deletes these. Fix later
    sp.Popen(['rm -rf {}.bm'.format(new_name)], shell=True)
    sp.Popen(['rm -rf {}.cl'.format(new_name)], shell=True)
    sp.Popen(['rm -rf {}.mp'.format(new_name)], shell=True)


def run_full_pipeline():
    """Run the whole thing.

    Note that this no longer produces both cut and uncut output; since the cut
    happens much earlier, it now only produces one or the other (depending
    on whether or not cut_baselines is true.)
    The Process:
        - casa_sequence():
            - cvel the cont-sub'ed dataset from jonas/raw_data to here.
            - split out the 50 channels around restfreq
            - convert that .ms to a .uvf
        - var_vis(): pull in that .uvf, add variances, resulting in another uvf
        - convert that to a vis
        - icr that vis to get a cm
        - cm to fits; now we have mol.{{uvf, vis, fits, cm}}
        - delete the clutter files: _split, _cvel, _exportuvfits, bm, cl, mp
    """
    t0 = time.time()
    mol = raw_input('Which line (HCN, HCO, CS, or CO)?\n').lower()
    cut = raw_input('Cut baselines for better signal (y/n)?\n').lower()
    cut_baselines = True if cut == 'y' else False
    remake = raw_input('Remake everything (y/n)? (Not functional rn)\n')
    remake_all = True if remake == 'y' else False

    # Paths to the data
    jonas = '/Volumes/disks/jonas/'
    raw_data_path = jonas + 'raw_data/'
    final_data_path = jonas + 'freshStart/modeling/data/' + mol + '/'
    name = mol
    if cut_baselines is True:
        name += '-short' + str(lines[mol]['baseline_cutoff'])

    # Establish a string for the log file to be made at the end
    log = 'Files created on ' + today + '\n\n'

    if remake_all is True:
        # This doesn't work yet.
        print "Remaking everything; emptied line dir and remaking."
        sp.call(['rm -rf', '{}*'.format(final_data_path)], shell=True)
        log += "Full remake occured; all files are fresh.\n\n"
    else:
        log += "Some files already existed and so were not remade.\n"
        log += "Careful for inconsistencies.\n\n"

    print "Now processing data...."
    casa_sequence(mol, raw_data_path,
                  final_data_path + name, cut_baselines)
    print "Finished casa_sequence()\n\n"

    print "Running varvis....\n\n"
    if already_exists(final_data_path + name + '.uvf') is False:
        # Note that var_vis takes in mol_exportuvfits, returns mol.uvf
        var_vis(final_data_path + name)
    print "Finished varvis; converting uvf to vis now....\n\n"
    # These are HCO specific rn
    restfreq = lines[mol]['restfreq']

    # chan0_freq = 356.718882
    f = fits.getheader(final_data_path + name + '.uvf')
    chan0_freq = (f['CRVAL4'] - (f['CRPIX4']-1) * f['CDELT4']) * 1e-9

    # Using the same math as in lines 130-135
    chan0_vel = 3e5 * (chan0_freq - restfreq)/restfreq
    data, header = fits.getdata(final_data_path + name + '.uvf', header=True)
    header['RESTFREQ'] = restfreq * 1e9
    fits.writeto(final_data_path + name + '.uvf', data, header, overwrite=True)
    if already_exists(final_data_path + name + '.vis') is False:
        sp.Popen(['fits',
                  'op=uvin',
                  'in={}.uvf'.format(name),
                  'velocity=lsr,{},1'.format(chan0_vel),
                  'out={}.vis'.format(name)],
                 cwd=final_data_path).wait()

    """
    # Cut out baselines.
    if b_min != 0:
        print "Cutting out baselines below", b_min
        # uvaver(mol)
        log += 'These visibilities were cut at' + str(b_min) + '\n'
    """

    print "Convolving data to get image, converting output to .fits\n\n"
    if already_exists(final_data_path + name + '.cm') is False:
        icr(final_data_path + name, mol=mol)

    print "Deleting the junk process files...\n\n"
    # Clear out the bad stuff. There's gotta be a better way of doing this.
    sp.Popen(['rm -rf {}.bm'.format(name)], shell=True, cwd=final_data_path)
    sp.Popen(['rm -rf {}.cl'.format(name)], shell=True, cwd=final_data_path)
    sp.Popen(['rm -rf {}.mp'.format(name)], shell=True, cwd=final_data_path)

    sp.Popen(['rm -rf {}_cvel.*'.format(name)], shell=True,
             cwd=final_data_path)
    sp.Popen(['rm -rf {}_split.*'.format(name)], shell=True,
             cwd=final_data_path)
    sp.Popen(['rm -rf {}_exportuvfits.*'.format(name)],
             shell=True, cwd=final_data_path)
    sp.Popen(['rm -rf casa*.log'], shell=True, cwd=final_data_path)

    tf = time.time()
    t_total = (tf - t0)/60
    log += '\nThis processing took' + str(t_total) + 'minutes.'
    with open(final_data_path + 'file_log.txt', 'w') as f:
        f.write(log)

    print "All done! This processing took " + str(t_total) + " minutes."


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process the data.')
    parser.add_argument('-r', '--run', action='store_true',
                        help='Run the processor.')
    args = parser.parse_args()
    if args.run:
        run_full_pipeline()










# The End
