"""A place to put all the junky equations I don't want elsewhere.

FOR GRID SEARCH.
"""

from astropy.io import fits
import numpy as np
import datetime


mol = 'hco'

# DATA FILE NAME
dataPath = 'data/' + mol + '/' + mol + '_short110'

# What day is it? Used to ID files.
months = ['jan', 'feb', 'march', 'april', 'may',
          'june', 'july', 'aug', 'sep', 'oct', 'nov', 'dec']
td = datetime.datetime.now()
today = months[td.month - 1] + str(td.day)

# These frequencies come from Splatalogue and are different than those
# embedded in, for example, the uvf file imported as hdr below
# which gives restfreq(hco) = 356.72278845870005

lines = {'hco': {'restfreq': 356.73422300,
                 'jnum': 3,
                 'rms': 1,
                 'chan_dir': 1,
                 'baseline_cutoff': 110,
                 'chan0': 355.791034},
         'hcn': {'restfreq': 354.50547590,
                 'jnum': 3,
                 'rms': 1,
                 'chan_dir': 1,
                 'baseline_cutoff': 0,
                 'chan0': 354.2837},
         'co': {'restfreq': 345.79598990,
                'jnum': 2,
                'rms': 1,
                'chan_dir': -1,
                'baseline_cutoff': 90,
                'chan0': 346.114523},
         'cs': {'restfreq': 342.88285030,
                'jnum': 6,
                'rms': 1,
                'chan_dir': -1,
                'baseline_cutoff': 25,
                'chan0': 344.237292},
         }


# Just the rest frequencies. I don't think these are used anywhere anymore.
restfreqs = {'hco': 356.73422300,
             'hcn': 354.50547590,
             'co': 345.79598990,
             'cs': 342.88285030
             }

# Column density [low, high]
col_dens = [1.3e21/(1.59e21), 1e30/(1.59e21)]
# Freeze out temp (K)
Tfo = 19
# Midplane temperature (K)
Tmid = 15
# Atmospheric temperature (K)
Tatm = 100
# Temp structure power law index ( T(r) ~ r^qq )
Tqq = -0.5
# Stellar mass, in solar masses [a,b]
m_star = [3.5, 0.4]
# Disk mass, in solar masses [a,b]
m_disk = [0.078, 0.028]
# Inner disk radius, in AU
r_in = [1., 1.]
# Outer disk radius, in AU
r_out = [500, 300]
# Handedness of rotation
rotHand = [-1, -1]

other_params = [col_dens, Tfo, Tmid, Tatm, Tqq, m_star, m_disk, r_in, r_out, rotHand]


def obs_stuff(mol):
    """Get freqs, restfreq, obsv, chanstep, both n_chans, and both chanmins.

    Just making this a function because it's ugly and line-dependent.
    """
    jnum = lines[mol]['jnum']
    # vsys isn't a function of molecule, but is needed here, so just keeping it
    vsys = [10.55, 10.85]

    # Dig some observational params out of the data file.
    hdr = fits.getheader('data/' + mol + '/' + mol + '.uvf')

    # restfreq = lines[mol]['restfreq']
    restfreq = hdr['CRVAL4'] * 1e-9

    # Each freq step:
    # arange( nchans + 1 - chanNum) * chanStepFreq + ChanNumFreq * Hz2GHz
    # I don't know why the arange is there, but it's making len(freqs)=51
    # That's not good, so I'm pulling it for now.
    freqs = ((np.arange(hdr['naxis4']) + 1 - hdr['crpix4']) * hdr['cdelt4'] + hdr['crval4']) * 1e-9
    # freqs = ((hdr['naxis4'] + 1 - hdr['crpix4']) * hdr['cdelt4'] + hdr['crval4']) * 1e-9

    # len(obsv) = 51; it's the velocity of each channel
    obsv = (restfreq-freqs)/restfreq * 2.99e5

    chanstep = lines[mol]['chan_dir'] * np.abs(obsv[1]-obsv[0])

    nchans_a = int(2*np.ceil(np.abs(obsv-vsys[0]).max()/np.abs(chanstep))+1)
    nchans_b = int(2*np.ceil(np.abs(obsv-vsys[1]).max()/np.abs(chanstep))+1)
    chanmin_a = -(nchans_a/2.-.5)*chanstep
    chanmin_b = -(nchans_b/2.-.5)*chanstep
    n_chans, chanmins = [nchans_a, nchans_b], [chanmin_a, chanmin_b]

    return [vsys, restfreq, freqs, obsv, chanstep, n_chans, chanmins, jnum]








# The end
