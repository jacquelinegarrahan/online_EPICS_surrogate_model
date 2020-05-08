import numpy as np
import math

from epics import caget, caput

from bokeh.driving import count
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.glyphs import MultiLine
from bokeh.models.glyphs import VArea


class pv_slider:
    def __init__(self, title, pvname, scale, start, end, step):

        self.pvname = pvname
        self.scale = scale

        self.slider = Slider(
            title=title, value=scale * caget(pvname), start=start, end=end, step=step
        )
        self.slider.on_change("value", self.set_pv_from_slider)

    def set_pv_from_slider(self, attrname, old, new):
        caput(self.pvname, new * self.scale)


pvs = ["phi(1)", "maxb(2)", "q_total", "sig_x"]
units = ["Deg", "T", "nC", "mm"]
ranges = [[-10.0, 10.0], [0.0, 0.1], [0.0, 0.3], [0.1, 0.5]]
prefix = "smvm:"

sliders = []

for ii, pv in enumerate(pvs):

    title = pv + " (" + units[ii] + ")"
    pvname = prefix + pv
    step = (ranges[ii][-1] - ranges[ii][0]) / 100.0

    pvs = pv_slider(
        title=title,
        pvname=pvname,
        scale=1,
        start=ranges[ii][0],
        end=ranges[ii][1],
        step=step,
    )
    sliders.append(pvs.slider)

scol = column(sliders, width=350)
curdoc().add_root(row(scol))

# curdoc().add_periodic_callback(update, 250)
curdoc().title = "Online Surrogate Model Virtual Machine"
