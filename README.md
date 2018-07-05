# Disk-Modeling
Code from my research working to characterize two protoplanetary disks in the Orion Nebula

##Directory Structure

It is expected that three directories already exist where these python files live: a git clone of Kevin Flaherty's disk_model, a directory called "data" which has subdirectories named for the emission line being observed (i.e. hco or cs), and one named "models" which will hold the files that are created by the runs.

When full_run is called, it sets up a subdir called 'run_[today's date]', symlinked over to iorek's scratch space to do the actual running on.


* full_run.py: Just calls the parameter-space walk-method (grid search or emcee) and sets up symlink
* grid_search.py: Executes a grid search. Includes:
    * gridSearch()
    * fullRun()
        * Writes out log files
* utils.py: All the helper/process functions that are called in the fitting process:
    * makeModel()
    * sumDisks()
    * chiSq
* constants.py: holds most the disk-specific constants and such stuff. Would like to have everything live here.
* run_params.py: holds the parameters for the grid search.
* tools.py: Some functions that are useful for things like plotting, convolving, and so on.
    * cgdisp(): Display channel maps. Options include cropping (2"x2" window) and contours (3, 6, 9 sigma)
    * imstat(): Make a dict out of the results from an imstat call. Returns rms and mean noise of the v=11.7 slice right now.
    * icr(): invert/clean/restor
    * imspec(): Get a spectrum
    * sample_model_in_uvplane(): fits to vis.
    * depickleLogFile(): read in the step log pickle that grid search makes.
    * uvaver(): cut baselines from the original data.
* centering_for_olay.cgdisp: a Miriad OLAY file, describing what part of the image to zoom in on.


##
