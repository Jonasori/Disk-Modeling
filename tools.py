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
import os
from constants import lines


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
    print '\nIMSTATING ', modelName, '\n'

    r_offsource = '(-5,-5,5,-1)'
    imstat_raw = sp.check_output(['imstat',
                                  'in={}{}'.format(modelName, ext),
                                  'region=arcsec,box{}'.format(r_offsource)
                                  ])
    imstat_out = imstat_raw.split('\n')
    # Get column names
    hdr = filter(None, imstat_out[11].split(' '))

    # Split the output on spaces and then drop empty elements.
    imstat_list = filter(None, imstat_out[plane_to_check].split(' '))

    """Sometimes the formatting gets weird and two elements get squished
        together. Fix this with the split loop below.

        Note that the form of the elements of an imstat is 1.234E-05,
        sometimes with a '-' out front. Therefore, each the length of each
        positive element is <= 9 and <= 10 for the negative ones.
        """
    for i in range(len(imstat_list)-1):
        if len(imstat_list[i]) > 11:
            if imstat_list[i][0] == '-':
                cut = 10
            else:
                cut = 9
            imstat_list.insert(i+1, imstat_list[i][cut:])
            imstat_list[i] = imstat_list[i][:cut]

    d = {}
    for i in range(len(hdr) - 1):
        d[hdr[i]] = imstat_list[i]
        print hdr[i], ': ', imstat_list[i]

    # Return the mean and rms
    return d
    # return float(d['Mean']), float(d['rms'])


# Invert/clean/restor: Take in a visibility, put out a convolved clean map.
def icr(visPath, mol, min_baseline=0, niters=1e4):
    """Invert/clean/restor: Turn a vis into a convolved clean map.

    .vis -> .bm, .mp, .cl, .cm, .fits
    Args:
        modelName (str): path to and name of the file. Do not include extension
        min_baseline (int): minimum baseline length to use. Cuts all below.
        niters (int): how many iterations of cleaning to run. Want this to be
                      big enough that it never gets triggered.
        rms (float): the the rms noise, to which we clean down to.
        mol (str): which molecule's restfreq to use.
    """
    print "\nConvolving image\n"

    # Since the path is sometimes more than 64 characters long, need to slice
    # it and use Popen/cwd to cut things down.
    # filepath = visPath.split('/')[1:-1]
    visName = visPath.split('/')[-1]
    filepath = visPath[:-len(visName)]

    # Add a shorthand name (easier to write)
    # Rename the outfile if we're cutting baselines and add the cut call.
    b = '' if min_baseline == 0 else min_baseline
    outName = visName + str(b)

    # Add restfreq to this vis
    rf = lines[mol]['restfreq']
    sp.Popen(['puthd',
              'in={}.vis/restfreq'.format(visName),
              'value={}'.format(rf)],
             stdout=open(os.devnull, 'wb'),
             cwd=filepath).wait()

    # Invert stuff:
    invert_str = ['invert',
                  'vis={}.vis'.format(visName),
                  'map={}.mp'.format(outName),
                  'beam={}.bm'.format(outName),
                  'options=systemp',
                  'cell=0.045',
                  'imsize=256',
                  'robust=2']

    if min_baseline != 0:
        invert_str.append('select=-uvrange(0,{})'.format(b))

    for end in ['cm', 'cl', 'bm', 'mp']:
        sp.Popen('rm -rf {}.{}'.format(outName, end),
                 shell=True, cwd=filepath).wait()
    print "Deleted", outName + '.[cm, cl, bm, mp]'

    # sp.call(invert_str, stdout=open(os.devnull, 'wb'))
    sp.Popen(invert_str, stdout=open(os.devnull, 'wb'), cwd=filepath).wait()

    # Grab the rms
    rms = imstat(filepath + outName, '.mp')[1]

    sp.Popen(['clean',
              'map={}.mp'.format(outName),
              'beam={}.bm'.format(outName),
              'out={}.cl'.format(outName),
              'niters={}'.format(niters),
              'threshold={}'.format(rms)],
             # stdout=open(os.devnull, 'wb')
             cwd=filepath).wait()

    sp.Popen(['restor',
              'map={}.mp'.format(outName),
              'beam={}.bm'.format(outName),
              'model={}.cl'.format(outName),
              'out={}.cm'.format(outName)],
             stdout=open(os.devnull, 'wb'),
             cwd=filepath).wait()

    sp.Popen(['fits',
              'op=xyout',
              'in={}.cm'.format(outName),
              'out={}.fits'.format(outName)],
             cwd=filepath).wait()


def sample_model_in_uvplane(modelPath, dataPath, mol='hco'):
    """Sample a model image in the uvplane given by the data.

    .fits -> {.im, .uvf, .vis}
    Args:
        modelPath (str): path to model fits file.
        dataPath (str): path to data vis file.
        mol (str): the molecule we're looking at.
    """
    remove(modelPath + '.im')
    sp.call(['fits', 'op=xyin',
             'in={}.fits'.format(modelPath),
             'out={}.im'.format(modelPath)])

    # Sample the model image using the observation uv coverage
    remove(modelPath + '.vis')
    sp.call(['uvmodel',
             'options=replace',
             'vis={}.vis'.format(dataPath),
             'model={}.im'.format(modelPath),
             'out={}.vis'.format(modelPath)])

    # Convert to UVfits
    remove(modelPath + '.uvf')
    sp.call(['fits',
             'op=uvout',
             'in={}.vis'.format(modelPath),
             'out={}.uvf'.format(modelPath)])

    print "completed sampling uvplane; created .im, .vis, .uvf\n\n"


def get_residuals(Name, mol='hco'):
    """Convert a fits file to im, vis, uvf.

    .fits -> {.im, .uvf, .vis}
    Note that this samples from hco.vis, so while it's basically
    general for my uses, it's not actually general.
    """
    data_vis = './data/' + mol + '/' + mol

    sp.call('rm -rf *{}.im'.format(Name), shell=True)

    sp.call(['fits', 'op=xyin',
             'in={}.fits'.format(Name),
             'out={}.im'.format(Name)])

    # Sample the model image using the observation uv coverage
    sp.call('rm -rf *{}.vis'.format(Name), shell=True)
    sp.call(['uvmodel',
             'options=subtract',
             'vis={}'.format(data_vis),
             'model={}.im'.format(Name),
             'out={}.vis'.format(Name + '_resid')])

    # Convert to UVfits
    sp.call('rm -rf *{}.uvf'.format(Name + '_resid'), shell=True)
    sp.call(['fits',
             'op=uvout',
             'in={}.vis'.format(Name + '_resid'),
             'out={}.uvf'.format(Name + '_resid')])


def imspec(imageName):
    """Drop a sweet spectrum. Takes in a .im."""
    sp.call(['imspec',
             'in={}'.format(imageName),
             'device=/xs, plot=sum'])


def already_exists(query):
    """Search an ls call to see if query is in it."""
    f = query.split('/')[-1]
    # path = query.split(f)[0]
    path = query[:-len(f)]

    print "Path is: ", path
    print "file is: ", f

    output = sp.check_output('ls', cwd=path).split('\n')

    if f in output:
        print query + ' alrady exists; skipping\n\n\n'
        return True
    else:
        print query + ' does not yet exist; executing command\n\n'
        return False


def remove(filePath):
    """Delete a file.

    Mostly just written to avoid having to remember the syntax every time.
    filePath is full filepath, including name and extension.
    Supports wildcards.
    """
    sp.Popen(['rm -rf {}'.format(filePath)], shell=True).wait()



# The End
