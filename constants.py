"""A place to put all the junky equations I don't want elsewhere.

FOR GRID SEARCH.
"""

from astropy.constants import c
from astropy.io import fits
import numpy as np
import datetime
c = c.to('km/s').value


mol = 'hco'

# These frequencies come from Splatalogue and are different than those
# embedded in, for example, the uvf file imported as hdr below
# which gives restfreq(hco) = 356.72278845870005

lines = {'hco': {'restfreq': 356.73422300,
                 'jnum': 3,
                 'rms': 1,
                 'chanstep_freq': 1 * 0.000488281,
                 'baseline_cutoff': 0,
                 'chan0_freq': 355.791034,
                 'spwID': 1},
         'hcn': {'restfreq': 354.50547590,
                 'jnum': 3,
                 'rms': 1,
                 'chanstep_freq': 1 * 0.000488281,
                 'baseline_cutoff': 0,
                 'chan0_freq': 354.2837,
                 'spwID': 0},
         'co': {'restfreq': 345.79598990,
                'jnum': 2,
                'rms': 1,
                'chanstep_freq': -1 * 0.000488281,
                'baseline_cutoff': 35,
                'chan0_freq': 346.114523,
                'spwID': 2},
         'cs': {'restfreq': 342.88285030,
                'jnum': 6,
                'rms': 1,
                'chanstep_freq': -1 * 0.000488281,
                'baseline_cutoff': 30,
                'chan0_freq': 344.237292,
                'spwID': 3}
         }

"""
headers = {'hco': {'im': fits.getheader('./data/hco/hco.fits'),
                   'vis': fits.getheader('./data/hco/hco.uvf')},
           'hcn': {'im': fits.getheader('./data/hcn/hcn.fits'),
                   'vis': fits.getheader('./data/hco/hcn.uvf')},
           'co': {'im': fits.getheader('./data/co/co.fits'),
                  'vis': fits.getheader('./data/co/co.uvf')},
           'cs': {'im': fits.getheader('./data//cs.fits'),
                  'vis': fits.getheader('./data/cs/cs.uvf')}
           }
"""

# DATA FILE NAME
def get_data_path(mol, short_vis_only=False):
    """Get the path to the data files for a given line."""
    dataPath = './data/' + mol + '/' + mol
    if short_vis_only is True:
        dataPath += '-short' + str(lines[mol]['baseline_cutoff'])
    return dataPath


dataPath = get_data_path(mol, short_vis_only=False)

# What day is it? Used to ID files.
months = ['jan', 'feb', 'march', 'april', 'may', 'june',
          'july', 'aug', 'sep', 'oct', 'nov', 'dec']
td = datetime.datetime.now()
today = months[td.month - 1] + str(td.day)


# DEFAULT VALUES
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
# Offsets (from center), in arcseconds
# centering_for_olay.cgdisp is the file that actually makes the green crosses!
# Williams values: offsets = [[-0.0298, 0.072], [-1.0456, -0.1879]]
# Fit values:
offsets = [[0.0002, 0.032], [-1.006, -0.318]]
# Williams vals: vsys = [10.55, 10.85]
vsys = [9.95, 10.75]


other_params = [col_dens, Tfo, Tmid, m_star, m_disk, r_in, rotHand, offsets]


def obs_stuff(mol):
    """Get freqs, restfreq, obsv, chanstep, both n_chans, and both chanmins.

    Just putting this stuff in a function because it's ugly and line-dependent.
    """
    jnum = lines[mol]['jnum']

    # Dig some observational params out of the data file.
    hdr = fits.getheader(dataPath + '.uvf')

    restfreq = lines[mol]['restfreq']
    # restfreq = hdr['CRVAL4'] * 1e-9

    # Get the frequencies and velocities of each step
    # {[arange(nchans) + 1 - chanNum] * chanStepFreq) + ChanNumFreq} * Hz2GHz
    # [-25,...,25] * d_nu + ref_chan_freq
    freqs = ( (np.arange(hdr['naxis4']) + 1 - hdr['crpix4']) * hdr['cdelt4'] + hdr['crval4']) * 1e-9
    obsv = c * (restfreq-freqs)/restfreq

    chan_dir = lines[mol]['chanstep_freq']/np.abs(lines[mol]['chanstep_freq'])
    chanstep = -1 * chan_dir * np.abs(obsv[1]-obsv[0])
    # chanstep = c * (lines[mol]['chanstep_freq']/lines[mol]['restfreq'])

    # Find the largest distance between a point on the velocity grid and sysv
    # Double it to cover both directions, convert from velocity to chans
    # The raytracing code will interpolate this (larger) grid onto the smaller
    # grid defined by nchans automatically.
    nchans_a = int(2*np.ceil(np.abs(obsv-vsys[0]).max()/np.abs(chanstep))+1)
    nchans_b = int(2*np.ceil(np.abs(obsv-vsys[1]).max()/np.abs(chanstep))+1)
    chanmin_a = -(nchans_a/2.-.5) * chanstep
    chanmin_b = -(nchans_b/2.-.5) * chanstep
    n_chans, chanmins = [nchans_a, nchans_b], [chanmin_a, chanmin_b]

    return [vsys, restfreq, freqs, obsv, chanstep, n_chans, chanmins, jnum]








# The end
