"""
Script some Miriad commands for easier calling, more specialized usage.

- cgdisp: Display a map.
- imstat: Get rms and mean noise from a plane of the image.
- imspec: Display a spectrum.
- icr (invert/clean/restor): Convolve a model with the beam.
- sample_model_in_uvplane: convert a model fits to a sampled map (im, vis, uvf)
- depickleLogFile: Unpack and process the log file from grid search.
"""

# Packages
import subprocess as sp
import pickle
import os


restfreqs = {'hco': 356.73422300,
             'hcn': 354.50547590,
             'co': 345.79598990,
             'cs': 342.88285030
             }


def cgdisp(imageName, crop=True, contours=True, rms=6.8e-3):
    """Drop some sweet chanmaps.

    Takes in an .im or .cm
    csize: 0 sets to default, and the third number controls 3pixel text size
    """
    if crop:
        r = '(-2,-2,2,2)'
    else:
        r = '(-5,-5,5,5)'
    if contours:
        sp.call(['cgdisp',
                 'in={},{}'.format(imageName, imageName),
                 'device=/xs',
                 'type=pix,con',
                 'region=arcsec,box{}'.format(r),
                 'olay={}'.format('centering_for_olay.cgdisp'),
                 'beamtyp=b,l,3',
                 'slev=a,{}'.format(rms),
                 'levs1=3,6,9',
                 'labtyp=arcsec,arcsec,abskms',
                 'options=3value,mirror,beambl',
                 'cols1=2',
                 'cols2=7',
                 'cols3=5',
                 'csize=0,0.7,0,0'
                 ])
    else:
        sp.call(['cgdisp',
                 'in={}'.format(imageName),
                 'device=/xs',
                 'region=arcsec,box{}'.format(r),
                 'olay={}'.format('centering_for_olay.cgdisp'),
                 'beamtyp=b,l,3',
                 'labtyp=arcsec,arcsec,abskms',
                 'options=3value',
                 'csize=0,0.7,0,0',
                 'cols1=2',
                 'cols2=7',
                 'cols3=5'
                 ])


def imstat(modelName, plane_to_check=30):
    """Call imstat to find rms and mean.

    Want an offsource region so that we can look at the noise. Decision to look
    at plane_to_check=30 is deliberate and is specific to this line of these
    data. Look at June 27 notes for justification of it.
    Args:
        modelName (str): name of the input file. Not necessarily a model.
        plane_to_check (int): Basically which channel to look at, but that
        this includes the ~10 header planes, too, so I think plane 30
        corresponds to channel 21 or so.
    """
    r_offsource = '(-5,-5,5,-1)'
    print '\n\nIMSTATING ', modelName
    imstat_raw = sp.check_output(['imstat',
                                  'in={}.cm'.format(modelName),
                                  'region=arcsec,box{}'.format(r_offsource)
                                  ])
    imstat_out = imstat_raw.split('\n')
    # Get column names
    hdr = filter(None, imstat_out[9].split(' '))

    # Split the output on spaces and then drop empty elements.
    imstat_list = filter(None, imstat_out[plane_to_check].split(' '))
    # A space gets crunched out between RMS and mean, so fix that:
    if len(imstat_list) == 7:
        imstat_list.insert(6, imstat_list[5][9:])
        imstat_list[5] = imstat_list[5][:9]

    d = {}
    for i in range(len(hdr) - 1):
        d[hdr[i]] = imstat_list[i]
        print hdr[i], ': ', imstat_list[i]

    # Return the mean and rms
    return float(d['Mean']), float(d['rms'])


# Invert/clean/restor: Take in a visibility, put out a convolved clean map.
# Note that right now the restfreq is HCO+ specific
def icr(modelName, min_baseline=0, niters=1e5, rms=3.33e-02, mol='hco'):
    """Invert/clean/restor: Turn a vis into a convolved clean map.

    Args:
        modelName (str): name of the file.
        min_baseline (int): minimum baseline length to use. Cuts all below.
        niters (int): how many iterations of cleaning to run. Want this to be
                      big enough that it never gets triggered.
        rms (float): the the rms noise, to which we clean down to.
        mol (str): which molecule's restfreq to use.
    """
    print "\nConvolving image\n"
    # Add a shorthand name (easier to write)
    b = min_baseline
    sp.call('rm -rf {}.cm'.format(modelName + str(b)), shell=True)
    sp.call('rm -rf {}.cl'.format(modelName + str(b)), shell=True)
    sp.call('rm -rf {}.bm'.format(modelName + str(b)), shell=True)
    sp.call('rm -rf {}.mp'.format(modelName + str(b)), shell=True)
    print "Deleted", modelName + str(b) + '*'

    # Add restfreq to this vis
    sp.call(['puthd',
             'in={}.vis/restfreq'.format(modelName),
             'value={}'.format(restfreqs[mol])
             ],
            stdout=open(os.devnull, 'wb'))

    if min_baseline == 0:
        # can't call select=-uvrange(0,0) so just get rid of that line for 0.
        # This way we also don't get files called data-hco0
        b = ''
        sp.call(['invert',
                 'vis={}.vis'.format(modelName),
                 'map={}.mp'.format(modelName),
                 'beam={}.bm'.format(modelName),
                 'options=systemp',
                 'cell=0.045',
                 'imsize=256',
                 'robust=2'],
                stdout=open(os.devnull, 'wb'))
    else:
        sp.call(['invert',
                 'vis={}.vis'.format(modelName),
                 'map={}.mp'.format(modelName + str(b)),
                 'beam={}.bm'.format(modelName + str(b)),
                 'options=systemp',
                 'select=-uvrange(0,{})'.format(b),
                 'cell=0.045',
                 'imsize=256',
                 'robust=2'],
                stdout=open(os.devnull, 'wb'))

    sp.call(['clean',
             'map={}.mp'.format(modelName + str(b)),
             'beam={}.bm'.format(modelName + str(b)),
             'out={}.cl'.format(modelName + str(b)),
             'niters={}'.format(niters),
             'threshold={}'.format(rms)
             ],
            stdout=open(os.devnull, 'wb'))

    sp.call(['restor',
             'map={}.mp'.format(modelName + str(b)),
             'beam={}.bm'.format(modelName + str(b)),
             'model={}.cl'.format(modelName + str(b)),
             'out={}.cm'.format(modelName + str(b))
             ],
            stdout=open(os.devnull, 'wb'))


def imspec(imageName):
    """Drop a sweet spectrum. Takes in a .im."""
    sp.call(['imspec',
             'in={}'.format(imageName),
             'device=/xs, plot=sum'])


def sample_model_in_uvplane(Name):
    """Convert a fits file to im, vis, uvf.

    .fits -> {.im, .uvf, .vis}
    Note that this samples from hco_viswvars, so while it's basically
    general for my uses, it's not actually general.
    """
    data_vis = 'hco_viswvars.vis'

    sp.call('rm -rf *{}.im'.format(Name), shell=True)

    sp.call(['fits', 'op=xyin',
             'in={}.fits'.format(Name),
             'out={}.im'.format(Name)])

    # Sample the model image using the observation uv coverage
    sp.call('rm -rf *{}.vis'.format(Name), shell=True)
    sp.call(['uvmodel',
             'options=replace',
             'vis={}'.format(data_vis),
             'model={}.im'.format(Name),
             'out={}.vis'.format(Name)])

    # Convert to UVfits
    sp.call('rm -rf *{}.uvf'.format(Name), shell=True)
    sp.call(['fits',
             'op=uvout',
             'in={}.vis'.format(Name),
             'out={}.uvf'.format(Name)])


def depickleLogFile(filename):
    """Read in the pickle'd full-log file from a run."""
    df = pickle.load(open('{}_step-log.pickle'.format(filename), 'rb'))
    # Note that we can find the min Chi2 val with:
    # m = df.set_index('Reduced Chi2').loc[min(df['Reduced Chi2'])]
    # This indexes the whole df by RedX2 and then finds the values that
    # minimize that new index.
    # Note, too, that it can be indexed either by slicing or by keys.
    df_a, df_b = df.loc['A', :], df.loc['B', :]
    min_X2_a = min(df_a['Reduced Chi2'])
    min_X2_b = min(df_b['Reduced Chi2'])
    # These come out as length-1 dicts
    best_fit_a = df_a.loc[df_a['Reduced Chi2'] == min_X2_a]
    best_fit_b = df_b.loc[df_b['Reduced Chi2'] == min_X2_b]

    out = {'full_log': df,
           'Disk A log': df_a,
           'Disk B log': df_b,
           'Best Fit A': best_fit_a,
           'Best Fit B': best_fit_b
           }
    return out


# The End
