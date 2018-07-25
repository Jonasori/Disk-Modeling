"""Data processing pipeline.

A small change
To be run from /Volumes/disks/jonas/freshStart/modeling
sp.Popen vs sp.call: Popen lets you change working directory for the call with
                     cwd arg, call blocks further action until its action is
                     complete, although Popen can be made to block with .wait()
"""


import subprocess as sp
from constants import lines, today, mol
from var_vis import var_vis
from tools import icr, already_exists
import argparse


def pipe(commands):
    """Translate a set of arguments into a CASA command, written by Cail."""
    call_string = '\n'.join([command if type(command) is str else '\n'.join(command) for command in commands])

    print('Piping the following commands to CASA:\n')
    print(call_string)
    # sp.call(['casa', '-c', call_string])
    sp.Popen(['casa', '-c', call_string]).wait()

    # clean up .log files that casa poops out
    sp.Popen('rm -rf *.log', shell=True).wait()


def casa_sequence(mol, split_range, raw_data_path,
                  output_path, remake_all=False):
    """Cvel, split, and export as uvf the original cont-sub'ed .ms.

    Args:
        - mol:
        - split_range:
        - raw_data_path:
        - output_path: path, with name included
        - remake_all (bool): if True, remove delete all pre-existing files.
    """
    if already_exists(output_path + '_cvel.ms') is False:
        pipe(["cvel(",
              "vis='{}calibrated-{}.ms.contsub',".format(raw_data_path, mol),
              "outputvis='{}_cvel.ms',".format(output_path),
              "field='OrionField4',",
              "restfreq='{}GHz',".format(lines[mol]['restfreq']),
              "outframe='LSRK')"
              ])

    if already_exists(output_path + '_split.ms') is False:
        spw = '*:' + str(split_range[0]) + '~' + str(split_range[1])
        pipe(["split(",
              "vis='{}_cvel.ms',".format(output_path),
              "outputvis='{}_split.ms',".format(output_path),
              "spw='{}',".format(spw),
              "datacolumn='data',",
              "keepflags=False)"
              ])

    if already_exists(output_path + '_exportuvfits.uvf') is False:
        pipe(["exportuvfits(",
              "vis='{}_split.ms',".format(output_path),
              "fitsfile='{}_exportuvfits.uvf')".format(output_path)
              ])


def find_split_cutoffs(mol, other_restfreq=0):
    """Find the indices of the 50 channels around the restfreq.

    chan_dir, chan0, nchans, chanstep from
    listobs(vis='mol.ms', field='OrionField4')
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

    split_range = [loc - 25, loc + 25]
    return split_range


def uvaver(mol):
    """Cut a vis file.

    This one uses Popen and cwd (change working directory) because the path was
    getting to be longer than buffer's 64-character limit. Could be translated
    to other funcs as well, but would just take some work.
    """
    filepath = './data/' + mol + '/'
    min_baseline = lines[mol]['baseline_cutoff']
    name = mol
    new_name = name + '-short' + str(min_baseline)

    """
    if already_exists(filepath + new_name + '.cm') is True:
        return "This vis is already fully cut; aborting."
    else:
        sp.Popen(['rm -rf ./*'], shell=True, cwd=filepath).wait()
    """

    print "\nStarting uvaver on ", new_name, '\n'
    sp.Popen(['uvaver',
              'vis={}.vis'.format(name),
              'select=-uvrange(0,{})'.format(min_baseline),
              'out={}.vis'.format(new_name)],
             cwd=filepath).wait()

    print "\nCompleted uvaver; starting fits uvout\n"
    sp.call(['fits',
             'op=uvout',
             'in={}.vis'.format(new_name),
             'out={}.uvf'.format(new_name)],
            cwd=filepath)

    print "\nCompleted fits uvout; starting ICR\n\n"
    icr(filepath + new_name, mol)

    # For some reason icr is returning and so it never deletes these. Fix later
    sp.Popen(['rm -rf {}.bm'.format(new_name)], shell=True)
    sp.Popen(['rm -rf {}.cl'.format(new_name)], shell=True)
    sp.Popen(['rm -rf {}.mp'.format(new_name)], shell=True)


def run_full_pipeline(mol, remake_all=True):
    """Run the whole thing.

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
    # Paths to the data
    jonas = '/Volumes/disks/jonas/'
    raw_data_path = jonas + 'raw_data/'
    final_data_path = jonas + 'freshStart/modeling/data/' + mol + '/'
    name = mol

    # Establish a string for the log file to be made at the end
    log = 'Files created on ' + today + '\n\n'

    if remake_all is True:
        print "Remaking everything; emptied line dir and remaking."
        sp.call(['rm -rf', '{}*'.format(final_data_path)], shell=True)
        log += "Full remake occured; all files are fresh.\n\n"
    else:
        log += "Some files already existed and so were not remade.\n"
        log += "Careful for inconsistencies.\n\n"

    b_min = lines[mol]['baseline_cutoff']
    split_range = find_split_cutoffs(mol)

    print "Split range is ", str(split_range[0]), str(split_range[1])
    print "Now processing data...."
    casa_sequence(mol, split_range, raw_data_path, final_data_path + name)
    log = log + 'Split range used: ' + str(split_range) + '\n'
    print "Finished casa_sequence()\n\n"

    print "Running varvis....\n\n"
    if already_exists(final_data_path + name + '.uvf') is False:
        # Note that var_vis takes in mol_exportuvfits, returns mol.uvf
        var_vis(final_data_path + name)

    print "Finished varvis; converting uvf to vis now....\n\n"
    if already_exists(final_data_path + name + '.vis') is False:
        sp.Popen(['fits',
                  'op=uvin',
                  'in={}.uvf'.format(name),
                  'out={}.vis'.format(name)],
                 cwd=final_data_path).wait()

    if b_min != 0:
        print "Cutting out baselines below", b_min
        uvaver(mol)
        log += 'These visibilities were cut at' + str(b_min) + '\n'

    print "Convolving data to get image, converting output to .fits\n\n"
    if already_exists(final_data_path + name + '.cm') is False:
        icr(final_data_path + name, mol=mol)

    print "Deleting the junk process files...\n\n"
    # Clear out the bad stuff. There's gotta be a better way of doing this.
    sp.Popen(['rm -rf {}.bm'.format(name)],
             shell=True, cwd=final_data_path)
    sp.Popen(['rm -rf {}.cl'.format(name)],
             shell=True, cwd=final_data_path)
    sp.Popen(['rm -rf {}.mp'.format(name)],
             shell=True, cwd=final_data_path)

    sp.Popen(['rm -rf {}_cvel.*'.format(name)],
             shell=True, cwd=final_data_path)
    sp.Popen(['rm -rf {}_split.*'.format(name)],
             shell=True, cwd=final_data_path)
    sp.Popen(['rm -rf {}_exportuvfits.*'.format(name)],
             shell=True, cwd=final_data_path)
    sp.Popen(['rm -rf casa*.log'], shell=True, cwd=final_data_path)

    with open(final_data_path + 'file_log.txt', 'w') as f:
        f.write(log)

    print "All done!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process the data.')
    parser.add_argument('-r', help='Run the processor.')
    args = parser.parse_args()

    if args.run:
        run_full_pipeline(mol)










# The End
