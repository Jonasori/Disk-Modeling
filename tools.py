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
from constants import restfreqs


def cgdisp(imageName, crop=True, contours=True, rms=6.8e-3):
    """Drop some sweet chanmaps.

    Args:
        imageName (str): name of the image to view, including .im or .cm
        crop (bool): whether or not to show constained image.
        contours (bool): whether or not to show 3-, 6-, and 9-sigma contours.
        rms (float): value to use for sigma.

    csize: 0 sets to default, and the third number controls 3pixel text size
    """
    if crop:
        r = '(-2,-2,2,2)'
    else:
        r = '(-5,-5,5,5)'

    call_str = ['cgdisp',
                'in={}'.format(imageName),
                'device=/xs',
                'region=arcsec,box{}'.format(r),
                'olay={}'.format('centering_for_olay.cgdisp'),
                'beamtyp=b,l,3',
                'labtyp=arcsec,arcsec,abskms',
                'options=3value',
                'csize=0,0.7,0,0'
                ]

    if contours:
        call_str[1] = 'in={},{}'.format(imageName, imageName)
        call_str.append('type=pix,con')
        call_str.append('slev=a,{}'.format(rms))
        call_str.append('levs1=3,6,9')
        call_str.append('options=3value,mirror,beambl')

    sp.call(call_str)
    """
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
    """


def imstat(modelName, ext='.cm', plane_to_check=30):
    """Call imstat to find rms and mean.

    Want an offsource region so that we can look at the noise. Decision to look
    at plane_to_check=30 is deliberate and is specific to this line of these
    data. Look at June 27 notes for justification of it.
    Args:
        modelName (str): name of the input file. Not necessarily a model.
                         MUST INCLUDE FILE EXTENSION
        plane_to_check (int): Basically which channel to look at, but that
        this includes the ~10 header planes, too, so I think plane 30
        corresponds to channel 21 or so.
    """
    r_offsource = '(-5,-5,5,-1)'
    print '\n\nIMSTATING ', modelName
    imstat_raw = sp.check_output(['imstat',
                                  'in={}{}'.format(modelName, ext),
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
def icr(modelName, min_baseline=0, niters=1e4, mol='hco'):
    """Invert/clean/restor: Turn a vis into a convolved clean map.

    Args:
        modelName (str): name of the file. Do not include extension.
        min_baseline (int): minimum baseline length to use. Cuts all below.
        niters (int): how many iterations of cleaning to run. Want this to be
                      big enough that it never gets triggered.
        rms (float): the the rms noise, to which we clean down to.
        mol (str): which molecule's restfreq to use.
    """
    print "\nConvolving image\n"

    # Add a shorthand name (easier to write)
    # Rename the outfile if we're cutting baselines and add the cut call.
    b = min_baseline
    if min_baseline != 0:
        modelName += str(b)

    # Add restfreq to this vis
    sp.call(['puthd',
             'in={}.vis/restfreq'.format(modelName),
             'value={}'.format(restfreqs[mol])
             ],
            stdout=open(os.devnull, 'wb'))

    invert_str = ['invert',
                  'vis={}.vis'.format(modelName),
                  'map={}.mp'.format(modelName),
                  'beam={}.bm'.format(modelName),
                  'options=systemp',
                  'cell=0.045',
                  'imsize=256',
                  'robust=2']

    # Should find a way to join this and the same conditional above.
    if min_baseline != 0:
        invert_str.append('select=-uvrange(0,{})'.format(b))


    for end in ['cm', 'cl', 'bm', 'mp']:
        sp.call('rm -rf {}.{}'.format(modelName, end), shell=True)
    print "Deleted", modelName + '.[cm, cl, bm, mp]'

    # Run invert
    sp.call(invert_str, stdout=open(os.devnull, 'wb'))

    # Grab the rms
    rms = imstat(modelName, '.mp')[1]
    sp.call(['clean',
             'map={}.mp'.format(modelName),
             'beam={}.bm'.format(modelName),
             'out={}.cl'.format(modelName),
             'niters={}'.format(niters),
             'threshold={}'.format(rms)]
            # stdout=open(os.devnull, 'wb')
            )

    sp.call(['restor',
             'map={}.mp'.format(modelName),
             'beam={}.bm'.format(modelName),
             'model={}.cl'.format(modelName),
             'out={}.cm'.format(modelName)
             ],
            stdout=open(os.devnull, 'wb'))

    sp.call(['fits',
             'op=xyout',
             'in={}.cm'.format(modelName),
             'out={}.fits'.format(modelName)
             ])


def imspec(imageName):
    """Drop a sweet spectrum. Takes in a .im."""
    sp.call(['imspec',
             'in={}'.format(imageName),
             'device=/xs, plot=sum'])


def sample_model_in_uvplane(Name):
    """Convert a fits file to im, vis, uvf.

    .fits -> {.im, .uvf, .vis}
    Note that this samples from hco.vis, so while it's basically
    general for my uses, it's not actually general.
    """
    data_vis = 'data/hco/hco.vis'

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


def uvaver(filepath, name, min_baseline):
    """Cut a vis file.

    This one uses Popen and cwd (change working directory) because the path was
    getting to be longer than buffer's 64-character limit. Could be translated
    to other funcs as well, but would just take some work.

    This also relies on the filename being the last three characters of the
    path, or could be changed to require that path and name be given
    separately. Neither seems great.
    """
    new_name = name + '-short' + str(min_baseline)

    if already_exists(filepath + new_name + '.vis') is True:
        return "This vis cut already exists; aborting."

    sp.Popen(['uvaver',
              'vis={}.vis'.format(name),
              'select=-uvrange(0,{})'.format(min_baseline),
              'out={}.vis'.format(new_name)],
             cwd=filepath)

    sp.call(['fits',
             'op=uvout',
             'in={}.vis'.format(new_name),
             'out={}.uvf'.format(new_name)],
            cwd=filepath)


def already_exists(query):
    """Search an ls call to see if query is in it."""
    f = query.split('/')[-1]
    path = query.split(f)[0]

    print "Path is: ", path
    print "file is: ", f

    output = sp.check_output('ls', cwd=path).split('\n')

    if f in output:
        print query + ' alrady exists; skipping\n\n\n'
        return True
    else:
        print query + ' does not yet exist; executing command\n\n'
        return False













# The End
