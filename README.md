# Disk-Modeling
Code from my research working to characterize two protoplanetary disks in the Orion Nebula

Hopefully I'll rewrite this more beautifully soon, but for now, here's the ugly version.

File Structure
* full_run.py: Just calls the parameter-space walk-method (grid search or emcee). This can maybe be eliminated
* grid_search.py: Executes a grid search. Includes:
    *  gridSearch() 
    * fullRun()
        * Writes out model_date-[long & short].log
* utils.py: All the helper/process functions that are called in the fitting process: 
    * makeModel()
    * sumDisks()
    * chiSq
    * It also holds all the disk-specific constants and such stuff. Maybe they should be elsewhere?
* run_params.py: holds the actual run parameters.
* tools.py: Some functions that are useful for things like plotting, convolving, and so on.
* centering_for_olay.cgdisp: a Miriad OLAY file, describing what part of the image to zoom in on.
