## Installation
Dependencies for running the example include:
tensorflow version 1.15 keras version 2.2.4.
keras version 2.2.4.
pyepics
pcaspy
h5py
bokeh 

pcaspy requires an EPICS install and has instructions on its website:
https://pcaspy.readthedocs.io/en/latest/

## Run
from the command line execute:

`python online_surrogate_model.py`

This will start an EPICS server with the model inputs and outputs as normal EPICS pvs:
`caput smvm:phi(1) 0.1`

You can monitor the model output PVs as usual:
`camonitor smvm:x_95coremit`

You'll see that this value has noise added on.
The noise parameter are set by additional EPICS records
`caput OUTPUT_PVNAME:sigma`

For the bokeh interactive sliders and striptool, run in a separate command line
`bokeh serve controls.py striptool.py`

Open two webroswer windows. In each one navigate to http://localhost:5006/controls and http://localhost:5006/striptool.  This should start the bokeh servers
The controls tab has sliders for the surrogate model inputs, and the striptool shows one example of the model outputs, with noise added


