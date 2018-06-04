"""
Turn some Miriad commands/sequences into python commands so that a) they can be
run from iPython more easily and b) so that they're just easier to run
(looking at you, icr())
"""

# Packages
import os, sys, datetime
from disk import *
import raytrace as rt
from astropy.io import fits
import numpy as np
import subprocess as sp
import astropy.units as u



# Drop some sweet chanmaps
# Takes in an .im or .cm
# csize: 0 sets to default, and the third number controls 3pixel text size
r = '(-2,-2,2,2)'
def cgdisp_no_contours(imageName):
    sp.call(['cgdisp',
        'in={}'.format(imageName),
        'device=/xs',
        'region=arcsec,box{}'.format(r),
        'olay={}'.format('centering_for_olay.cgdisp'),
	'beamtyp=b,l,3',
	'labtyp=arcsec,arcsec,abskms',
	'options=3value',
	'csize=0,0.7,0,0'])


r = '(-2,-2,2,2)'
def cgdisp(imageName, contours=True):
    if contours==True:
	sp.call(['cgdisp',
        	'in={},{}'.format(imageName,imageName),
	        'device=/xs',
		'type=pix,con',
	        'region=arcsec,box{}'.format(r),
	        'olay={}'.format('centering_for_olay.cgdisp'),
	        'beamtyp=b,l,3',
		'slev=a,6.8e-3',
		'levs1=2,3,4,5,6,7,8,9',
	        'labtyp=arcsec,arcsec,abskms',
        	'options=3value,mirror,beambl',
        	'csize=0,0.7,0,0'])
    else:
	sp.call(['cgdisp',
        	'in={}'.format(imageName),
        	'device=/xs',
        	'region=arcsec,box{}'.format(r),
        	'olay={}'.format('centering_for_olay.cgdisp'),
        	'beamtyp=b,l,3',
        	'labtyp=arcsec,arcsec,abskms',
        	'options=3value',
        	'csize=0,0.7,0,0'])	




# Drop a sweet spectrum
# Takes in a .im

def imspec(imageName):
    sp.call(['imspec',
        'in={}'.format(imageName),
        'device=/xs, plot=sum'])


# Invert/clean/restor: Take in a visibility, put out a convolved clean map.
def icr(modelName):
    print "\n\nEntering icr()\n\n"
    sp.call('rm -rf {}.mp'.format(modelName), shell=True)
    sp.call('rm -rf {}.bm'.format(modelName), shell=True)
    sp.call('rm -rf {}.cl'.format(modelName), shell=True)
    sp.call('rm -rf {}.cm'.format(modelName), shell=True)

    # Add restfreq to this vis
    sp.call(['puthd',
	'in={}.vis/restfreq'.format(modelName),
	'value=356.73422300'])

    sp.call(['invert',
        'vis={}.vis'.format(modelName),
        'map={}.mp'.format(modelName),
        'beam={}.bm'.format(modelName),
        'options=systemp',
	'cell=0.045',
	'imsize=256',
        'robust=2'])

    sp.call(['clean',
        'map={}.mp'.format(modelName),
        'beam={}.bm'.format(modelName),
        'out={}.cl'.format(modelName),
        'niters=10000',
	'threshold=1.3e-2'])

    sp.call(['restor',
        'map={}.mp'.format(modelName),
        'beam={}.bm'.format(modelName),
        'model={}.cl'.format(modelName),
        'out={}.cm'.format(modelName)])


# Convert a fits file to im,vis,uvf
# .fits -> {.im, .uvf, .vis}
def im2vis(Name):
    print "\n\nEntering im2vis()\n\n"
    # Note that this samples from hco_viswvars, so while it's basically general for my uses, it's not actually general.
    data_vis = "hco_viswvars.vis"


    sp.call('rm -rf *{}.im'.format(Name), shell=True)
    sp.call(['fits', 'op=xyin',
        'in={}.fits'.format(Name),
        'out={}.im'.format(Name)])

    # Sample the model image using the observation uv coverage
    sp.call('rm -rf *{}.vis'.format(Name), shell=True)
    sp.call(['uvmodel', 'options=replace',
        'vis={}'.format(data_vis),
        'model={}.im'.format(Name),
        'out={}.vis'.format(Name)])

    #Convert to UVfits
    sp.call('rm -rf *{}.uvf'.format(Name), shell=True)
    sp.call(['fits', 'op=uvout',
        'in={}.vis'.format(Name),
        'out={}.uvf'.format(Name)])



# Turn a model fits file into an image and view it (using cgdisp())
# .fits -> .im
def visualizeFitsToIm(name):
    print "\n\nEntering visualizeFitsToIm()\n\n"
    # Grab header from the appropriate FITS data file to use on the model.
    data_for_header=fits.open('../data/hco.fits')
    #data_for_header=fits.open('hco_viswvars.uvf')
    heady = data_for_header[0].header
    data_for_header.close()

    fits_data = fits.getdata(name + '.fits')
    im = fits.PrimaryHDU()                                  # blank HDU
    im.header = heady
    im.data = fits_data

    fitsout = name + '.fits'
    # Write it out to a file, overwriting the existing one if need be
    im.writeto(fitsout, overwrite=True)                             # overwrite used to be clobber

    # Make it into an image for viewing
    sp.call('rm -rf *{}.im'.format(name), shell=True)
    sp.call(['fits', 'op=xyin',
            'in={}.fits'.format(name),
            'out={}.im'.format(name)])

    image_name = name + '.im'
    cgdisp(image_name)



# Turn a model fits file into an image, convolve it with the beam, and view the result
# This function is bad and does some weird stuff. Just use ICR and look at the CM
# .fits -> {.im, .uvf, .vis, .mp, .bm, .cl, .cm, .fits}
def createConvolvedMap(fname):

    # Used to have a whole new file making process happening here. No idea why.

    # Get a vis from that image
    im2vis(fname)
    # Convolve that vis file with the beam, out a clean map (.cm)
    icr(fname)
    # Turn that .cm back to a .fits (useful for plotting)
    sp.call(['fits', 'op=xyout',
            'in={}.cm'.format(fname),
            'out={}_convolved.fits'.format(fname)])

    # Plotting needs the good header, so let's also get an image out.
    # Note that this also has a cgdisp call built in.
    visualizeFitsToIm(fname + '_convolved')







### MAKE CHANNEL MAPS ###
def makeResidualMap(modelDisk, dataDisk):
	# make sure to save as fig, not pop up. Probably
	# residMapName defined at the top, where all variables should be named.
	sp.call('cgdisp device={}.ps/ps in=data.cm,resid.cm type=pix,con slev=1.5e-5,a levs1=-2,2,4,6 nxy=5,4 options=full,beambl labtyp=arcsec'.format(residMapName), shell=True)




#The End
