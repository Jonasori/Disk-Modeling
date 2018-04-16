"""
Some nice functions to be used in making models
"""


################
### PACKAGES ###
################

import os, sys, datetime
from disk import *
import raytrace as rt
from astropy.io import fits
import numpy as np
import subprocess as sp
import astropy.units as u



# DATA FILE NAME
data_file = 'data-hco'


##########################
### CONSTANTS & PARAMS ###
##########################


col_dens = [1.3e21/(1.59e21), 1e30/(1.59e21)]           # Column density [low, high]
Tfo = 19                                                # Freeze out temp (K)
Tmid = 15                                               # Midplane temperature (K)
Tatm = 100                                              # Atmospheric temperature (K)
Tqq = -0.5                                              # Temp structure power law index ( T(r) ~ r^qq )
m_star = [3.5, 0.4]                                     # Stellar mass, in solar masses [a,b]
m_disk = [0.078, 0.028]                                 # Disk mass, in solar masses [a,b]
r_in = [1.,1.]                                          # Inner disk radius, in AU
r_out = [500,300]                                       # Outer disk radius, in AU
# Formerly [10.55, 10.85]
sysv = [10.55, 10.85]					# Systemic velocities, in km/s
rotHand = [1, -1]					# Handedness of rotation


# Offsets seem to be weird: x is negative (x=1 is on the left), and y is normal.
#offsets = [ [0.41, 0.1], [-0.6, -0.13] ] 		# Not sure where I got these numbers
offsets = [ [0,0], [-1.0512, -0.2916] ]			# Offsets (from center?), in arcseconds



# General constants
restfreq = 356.73422300					# GHz
# Lines 217-229 in Kevin's single_model.py are relevant here.

hdr = fits.getheader(data_file + '.uvf')
#Nchans = hdr['naxis4']
# Each freq step: arange( nchans + 1 - chanNum) * chanStepFreq + ChanNumFreq * Hz2GHz
freq = ((np.arange(hdr['naxis4']) + 1 - hdr['crpix4']) * hdr['cdelt4'] + hdr['crval4']) * 1e-9
# c * (restfreq - freq) / restfreq
obsv = (restfreq-freq)/restfreq*2.99e5
# Just change this since it's an actual run parameter

Chanstep = (-1)* np.abs(obsv[1]-obsv[0])


# Find the max spread between systemic velocity and observed channel velocity,
#	divide that by how big each channel step is, and double it
# Unclear why two of these are needed.
# np.abs in the denominator to keep nchans positive even when chanstep is negative
Nchans = [0,0]
Nchans[1] = int(2*np.ceil(np.abs(obsv-sysv[1]).max()/np.abs(Chanstep))+1)
Nchans[0] = int(2*np.ceil(np.abs(obsv-sysv[0]).max()/np.abs(Chanstep))+1)


# Specify each disks's min chan velocity
Chanmin = [0,0]
Chanmin[0] = -(Nchans[0]/2.-.5)*Chanstep
Chanmin[1] = -(Nchans[1]/2.-.5)*Chanstep






########################
### USEFUL FUNCTIONS ###
########################

### MAKE A SINGLE MODEL DISK ###
def makeModel(diskParams, outputName, DI):
	"""
		Takes:		diskParams: list of floats
					outputName: string. Should be consistent with other outputNames?
					DI: 0 or 1
		Returns:	Nothing
		Creates:	A model disk, named outputName.
		"""
	# DI = Disk Index: the index for the tuples below. 0=A, 1=B

	print "Entering makeModel()"

	# Clear out space
	# sp.call('rm -rf {}.{{fits,vis,uvf,im}}'.format(outputName), shell=True)

	Tatms = diskParams[0]
	Tqq = diskParams[1]
	Xmol = diskParams[2]								# Only an index, so must be raised as 10**Xmol
	RAout = diskParams[3]
	PA = diskParams[4]
	Incl = diskParams[5]

	a=Disk(params=[Tqq,
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

	# The data have 51 channels (from the casa split()), so nchans must be 51.
	rt.total_model(a, imres=0.1,
			nchans=Nchans[DI],
			chanmin=Chanmin[DI],
			chanstep=Chanstep,
			distance=414,
			xnpix = 128,
			vsys=sysv[DI],
			PA = PA,
			offs=offsets[DI],
			modfile=outputName,
			isgas=True,
			flipme=False,
			freq0=restfreq,
			Jnum=3,
			obsv=obsv)

	print "MakeModel() completed"
	print "using", PA, "as position angle"



### SUM TWO MODEL DISKS ###
def sumDisks(fileNameA, fileNameB, outputName):
	"""
	Takes:		fileNameA: name of file, not including .fits
				fileNameB: as above
				outputName: the name of the file to be exported, with no file-type endings.
	Returns:	None
	Creates:	outputName.[fits, im, vis, uvf]
	"""


	# Now sum them up and make a new fits file
	a=fits.getdata(fileNameA + '.fits')
	b=fits.getdata(fileNameB + '.fits')


	# The actual disk summing
	sum_data = a + b



	# There are too many variable names here and they're confusing. Gotta fix it.

	# Create the empty structure for the final fits file.
	im = fits.PrimaryHDU()
	# Add the data
	im.data = sum_data

	# Add the header. Kevin's code should populate the header more or less correctly, so pull a header from one of the models.
	header_info_from_model = fits.open(fileNameA + '.fits')
	model_header = header_info_from_model[0].header
	header_info_from_model.close()

	im.header = model_header

	# Now swap out some of the values using values from the data file:
	header_info_from_data = fits.open('../data/hco.fits')
  	data_header = header_info_from_data[0].header
    	header_info_from_data.close()

	im.header['CRVAL1'] = data_header['CRVAL1']
	im.header['CRVAL2'] = data_header['CRVAL2']
	#im.header['EPOCH'] = data_header['EPOCH']
	im.header['RESTFRQ'] = data_header['RESTFRQ']



	# Write it out to a file, overwriting the existing one if need be
	fitsout = outputName + '.fits'
	im.writeto(fitsout, overwrite=True)

	"""
	sp.call
	puthd in={fitsout.fits}/EPOCH value=2000.0
	"""


	# Clear out the old files to make room for the new
	sp.call('rm -rf {}.vis'.format(outputName), shell=True)
	sp.call('rm -rf {}.uvf'.format(outputName), shell=True)
	sp.call('rm -rf {}.im'.format(outputName), shell=True)

	# Now convert that file to the visibility domain:

	sp.call(['fits', 'op=xyin',
	    'in={}.fits'.format(outputName),
	    'out={}.im'.format(outputName)])

	# Sample the model image using the observation uv coverage
	sp.call(['uvmodel', 'options=replace',
	    'vis={}.vis'.format(data_file),
	    'model={}.im'.format(outputName),
	    'out={}.vis'.format(outputName)])

	#Convert to UVfits

	sp.call(['fits', 'op=uvout',
	    'in={}.vis'.format(outputName),
	    'out={}.uvf'.format(outputName)])




### CALCULATE  CHISQ BETWEEN MODEL AND DATA ###
def chiSq(infile):
	"""
	Takes: 		infile: file name of model to be compared, not including .fits
	Returns:	[Raw X2, Reduced X2]
	Creates: 	None
	"""

	# GET VISIBILITIES
	data = fits.open('./' + data_file + '.uvf')
	data_vis=data[0].data['data'].squeeze()

	model = fits.open(infile + '.uvf')
	model_vis=model[0].data['data'].squeeze()

	# PREPARE STUFF FOR CHI SQUARED
	# np.ravel flattens the [45xxx,1,1,1,51,2,3] array into a [234xxxx, 1] (1D) array.
	# Ordering: np.ravel([[1,2],[3,4]]) gives [1,3,2,4], so its flattening index-wise, rather than channel-wise (i.e. by col rather than row)

	# Turn polarized data to stokes
	
	"""
	data_real = np.ravel((data_vis[:,0,0,0,:,0,0] + data_vis[:,0,0,0,:,1,0])/2.0, order='F')
	data_imag = np.ravel((data_vis[:,0,0,0,:,0,1] + data_vis[:,0,0,0,:,1,1])/2.0, order='F')
	
	model_real = np.ravel(model_vis[::2,0,0,:,0,0],order='F')
	model_imag = np.ravel(model_vis[::2,0,0,:,0,1],order='F')
	
	print data_real.shape	
	wt = np.ravel(data_vis[:,0,0,0,:,0,2])
        loc = np.where(wt>0)
	"""
	
	# data_vis.squeeze(): [visibilities, channels, polarizations?, real/imaginary]	

	# Should the 2s be floats?
	data_real = (data_vis[:,:,0,0]+data_vis[:,:,1,0])/2.
	data_imag = (data_vis[:,:,0,1] + data_vis[:,:,1,1])/2. 
	
	# get real and imaginary values, skipping repeating values created by uvmodel.
	# when uvmodel converts to Stokes I, it either puts the value in place
        # of BOTH xx and yy, or makes xx and yy the same.
        # either way, selecting every other value solves the problem.	

	# These might not be right yet	
	# chiSq is coming out around 300, which seems way too high
	model_real = model_vis[::2,:,0]
	model_imag = model_vis[::2,:,1]

	wt = data_vis[:,:,0,2]
	loc = np.where(wt>0)

	raw_chi = np.sum( wt*(data_real - model_real)**2 ) + np.sum( wt*(data_imag - model_imag)**2 )

	# Degrees of freedom is how many total real and imaginary weights we've got.
	dof = 2*len(data_vis)
	red_chi = raw_chi/dof
	#return format([raw_chi, red_chi], 'f')
	return [raw_chi, red_chi]
