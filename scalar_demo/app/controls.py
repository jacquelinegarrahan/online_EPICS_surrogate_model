import numpy as np
import math

from p4p.client.thread import Context
from bokeh.driving import count
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.glyphs import MultiLine
from bokeh.models.glyphs import VArea

from scalar_demo import PVS, PREFIX


CONTEXT = Context("pva")


class pv_slider:
    def __init__(self, title, pvname, scale, start, end, step):

        self.pvname = pvname
        self.scale = scale

        val = CONTEXT.get(pvname)

        self.slider = Slider(
            title=title,
            value=scale * CONTEXT.get(pvname),
            start=start,
            end=end,
            step=step,
        )
        self.slider.on_change("value", self.set_pv_from_slider)

    def set_pv_from_slider(self, attrname, old, new):
        CONTEXT.put(self.pvname, new * self.scale)

sliders = []

for ii, pv in enumerate(PVS):

    title = pv + " (" + PVS[pv]["units"] + ")"
    pvname = PREFIX + ":" + pv
    step = (PVS[pv]["range"][1] - PVS[pv]["range"][0]) / 100.0

    pvs = pv_slider(
        title=title,
        pvname=pvname,
        scale=1,
        start=PVS[pv]["range"][0],
        end=PVS[pv]["range"][1],
        step=step,
    )
    sliders.append(pvs.slider)

scol = column(sliders, width=350)
curdoc().add_root(row(scol))

# curdoc().add_periodic_callback(update, 250)
curdoc().title = "Online Surrogate Model Virtual Machine"