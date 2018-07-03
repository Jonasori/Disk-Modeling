"""Some nice functions to be used in making models."""


############
# PACKAGES #
############

import numpy as np
import subprocess as sp
import disk_model.raytrace as rt
from astropy.io import fits
from disk_model.disk import Disk
from constants import obs_stuff, other_params
from full_run import mol


######################
# CONSTANTS & PARAMS #
######################

# DATA FILE NAME
dataPath = 'data/' + mol + '/' + mol

# Offsets (from center), in arcseconds
# centering_for_olay.cgdisp is the file that actually makes the green crosses!
offsets = [[-0.0298, 0.072], [-1.0456, -0.1879]]

vsys, restfreq, freq0, obsv, chanstep, n_chans, chanmins, jnum = obs_stuff(mol)
col_dens, Tfo, Tmid, Tatm, Tqq, m_star, m_disk, r_in, r_out, rotHand = other_params

# For some reason, CO and CS have channels that go backwards.
if mol == 'co' or mol == 'cs':
    # Maybe also switch chanmins?
    chanstep *= -1


####################
# USEFUL FUNCTIONS #
####################


def makeModel(diskParams, outputPath, DI):
    """Make a single model disk.

    Args:
        diskParams (list of floats): the physical parameters for the model.
        outputPath (str) The path to where created files should go.
        DI (0 or 1): the index of the disk being modeled.
    Creates:
        {outputPath}.fits, a single model disk.
    """
    # DI = Disk Index: the index for the tuples below. 0=A, 1=B

    print "Entering makeModel()"
    print outputPath

    # Clear out space
    # sp.call('rm -rf {}.{{fits,vis,uvf,im}}'.format(outputPath), shell=True)

    Tatms = diskParams[0]
    Tqq = diskParams[1]
    Xmol = diskParams[2]
    RAout = diskParams[3]
    PA = diskParams[4]
    Incl = diskParams[5]

    a = Disk(params=[Tqq,
                     m_disk[DI],
                     1.,
                     r_in[DI],
                     r_out[DI],
                     100,
                     Incl,
                     m_star[DI],
                     10**Xmol,
                     0.081,
                     70.,
                     Tmid,
                     Tatms,
                     col_dens,
                     [1., RAout],
                     rotHand[DI]])

    # The data have 51 channels (from the casa split()), so n_chans must be 51
    rt.total_model(a, imres=0.1,
                   nchans=n_chans[DI],
                   chanmin=chanmins[DI],
                   chanstep=chanstep,
                   distance=414,
                   xnpix=128,
                   vsys=vsys[DI],
                   PA=PA,
                   offs=offsets[DI],
                   modfile=outputPath,
                   isgas=True,
                   flipme=False,
                   freq0=restfreq,
                   Jnum=jnum,
                   obsv=obsv)

    print "MakeModel() completed"


# SUM TWO MODEL DISKS #
def sumDisks(filePathA, filePathB, outputPath):
    """Sum two model disks.

    Args:
        filePathA, filePathB (str): where to find the model files.
                                    Don't include the filetype extension.
        outputPath: the name of the file to be exported.
                    Don't include the filetype extension.
    Creates:	outputPath.[fits, im, vis, uvf]
    """
    # Now sum them up and make a new fits file
    a = fits.getdata(filePathA + '.fits')
    b = fits.getdata(filePathB + '.fits')

    # The actual disk summing
    sum_data = a + b

    # There are too many variable names here and they're confusing.

    # Create the empty structure for the final fits file and add the data
    im = fits.PrimaryHDU()
    im.data = sum_data

    # Add the header. Kevin's code should populate the header more or less
    # correctly, so pull a header from one of the models.
    header_info_from_model = fits.open(filePathA + '.fits')
    model_header = header_info_from_model[0].header
    header_info_from_model.close()

    im.header = model_header

    # Now swap out some of the values using values from the data file:
    header_info_from_data = fits.open(dataPath + '.fits')
    data_header = header_info_from_data[0].header
    header_info_from_data.close()

    im.header['CRVAL1'] = data_header['CRVAL1']
    im.header['CRVAL2'] = data_header['CRVAL2']
    im.header['RESTFRQ'] = data_header['RESTFRQ']
    # im.header['EPOCH'] = data_header['EPOCH']

    # Write it out to a file, overwriting the existing one if need be
    fitsout = outputPath + '.fits'
    im.writeto(fitsout, overwrite=True)

    # Clear out the old files to make room for the new
    sp.call('rm -rf {}.{{vis, uvf, im}}'.format(outputPath), shell=True)

    # Now convert that file to the visibility domain:
    sp.call(['fits', 'op=xyin',
             'in={}.fits'.format(outputPath),
             'out={}.im'.format(outputPath)])

    # Sample the model image using the observation uv coverage
    sp.call(['uvmodel', 'options=replace',
             'vis={}.vis'.format(dataPath),
             'model={}.im'.format(outputPath),
             'out={}.vis'.format(outputPath)])

    # Convert to UVfits
    sp.call(['fits', 'op=uvout',
             'in={}.vis'.format(outputPath),
             'out={}.uvf'.format(outputPath)])


def chiSq(infile):
    """Calculate chi-squared metric between model and data.

    Args:
        infile: file name of model to be compared, not including .fits
    Returns:	[Raw X2, Reduced X2]
    Creates: 	None
    """
    # GET VISIBILITIES
    data = fits.open(dataPath + '.uvf')
    data_vis = data[0].data['data'].squeeze()

    model = fits.open(infile + '.uvf')
    model_vis = model[0].data['data'].squeeze()

    # PREPARE STUFF FOR CHI SQUARED

    # Turn polarized data to stokes
    # data_vis.squeeze(): [visibilities, chans, polarizations?, real/imaginary]
    # Should the 2s be floats?
    data_real = (data_vis[:, :, 0, 0] + data_vis[:, :, 1, 0])/2.
    data_imag = (data_vis[:, :, 0, 1] + data_vis[:, :, 1, 1])/2.

    # get real and imaginary values, skipping repeating vals created by uvmodel
    # when uvmodel converts to Stokes I, it either puts the value in place
    # of BOTH xx and yy, or makes xx and yy the same.
    # either way, selecting every other value solves the problem.

    # These might not be right yet
    # chiSq is coming out around 300, which seems way too high
    model_real = model_vis[::2, :, 0]
    model_imag = model_vis[::2, :, 1]

    wt = data_vis[:, :, 0, 2]
    loc = np.where(wt > 0)

    raw_chi = np.sum(wt*(data_real - model_real)**2) + \
        np.sum(wt*(data_imag - model_imag)**2)

    # Degrees of freedom is how many total real and imaginary weights we've got.
    dof = 2*len(data_vis)
    red_chi = raw_chi/dof
    # return format([raw_chi, red_chi], 'f')
    return [raw_chi, red_chi]
