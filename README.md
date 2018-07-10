# Disk-Modeling
Code from my research working to characterize two protoplanetary disks in the Orion Nebula

## Directory Structure

It is expected that three directories already exist where these python files live:
- a git clone of Kevin Flaherty's disk_model
- a directory called "data" which has subdirectories named for the emission line being observed (i.e. hco or cs). This is where process_data.py deposits its work and where grid_search and others draw from.
- a directory named "models" containing run-specific directories to hold the files deposited by grid_search and others.
- a directory named "baselines" to hold noise-based baseline cutoff testing (run by baseline_cutoff.py)

All python files should live at the top level and be run out from there.

When full_run (which runs gridSearch) is called, it sets up a subdir called 'run_[today's date]', symlinked over to iorek's scratch space to do the actual running on. baseline_cutoff also sets up a symlink.


## What the Files Are and What they Do
* full_run.py: Just calls the parameter-space exploration method (grid search or MCMC) and sets up symlink. MCMC is not yet implemented but ultimately should be able to just be called directly out of this.
* grid_search.py: Executes a grid search. Includes:
    * gridSearch()
    * fullRun()
        * Writes out log files (no, it doesn't?)
* utils.py: Homemade helper functions for the grid search (as opposed to Python/package management functions in tools.py)
    * makeModel()
    * sumDisks()
    * chiSq
* tools.py: Some functions that are useful for things like plotting, convolving, and so on.
    * cgdisp(): Display channel maps. Options include cropping (2"x2" window) and contours (3, 6, 9 sigma)
    * imstat(): Make a dict out of the results from an imstat call. Returns rms and mean noise of the v=11.7 slice right now.
    * icr(): invert/clean/restor
    * imspec(): Get a spectrum
    * sample_model_in_uvplane(): fits to vis.
    * depickleLogFile(): read in the step log pickle that grid search makes.
    * uvaver(): cut baselines from the original data.
* centering_for_olay.cgdisp: a Miriad OLAY file, describing what part of the image to zoom in on.
* constants.py: holds most the disk-specific constants and such stuff. Would like to have all disk-specific values live here.
* run_params.py: holds the parameters for the grid search.
* baseline_cutoff.py: Convolve a bunch of images, cutting off different numbers of baselines off the bottom. Makes a plot of RMS and mean noise as functions of baseline cutoff.
* process_data.py: A data-processing pipeline to go form calibrated-mol.ms.contsub to final .vis, .uvf, and .fits files. Also produces a truncated .vis file chopped at the minimum baseline value as given by the "lines" dictionary in constants.py.



##
