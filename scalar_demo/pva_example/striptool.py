import numpy as np
import math
import time

from epics import caget, caput, PV

from bokeh.driving import count
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.glyphs import MultiLine


class pv_buffer:
    def __init__(self, pv, buffer_size):

        self.pvname = pv
        self.pv = PV(pv, auto_monitor=True)
        self.data = np.array([self.pv.get()])

        self.tstart = time.time()

        self.time = np.array([self.tstart])
        self.buffer_size = buffer_size

    def poll(self):

        t = time.time()
        v = caget(self.pvname)  # self.pv.get()

        # print(t,v)

        if len(self.data) < self.buffer_size:
            self.time = np.append(self.time, t)
            self.data = np.append(self.data, v)

        else:
            self.time[:-1] = self.time[1:]
            self.time[-1] = t
            self.data[:-1] = self.data[1:]
            self.data[-1] = v

        return self.time - self.tstart, self.data


pvbuffer = pv_buffer("smvm:x_95coremit", 100)
ts, ys = pvbuffer.poll()
source = ColumnDataSource(dict(x=ts, y=ys * 1e6))
p = figure(plot_width=400, plot_height=400, y_range=[0, 2])
p.line(x="x", y="y", line_width=2, source=source)
p.yaxis.axis_label = "x_95coreemit (microns)"
p.xaxis.axis_label = "time (sec)"


def update():

    ts, ys = pvbuffer.poll()
    ys = ys * 1e6
    source.data = dict(x=ts, y=ys)


curdoc().add_root(p)
curdoc().add_periodic_callback(update, 250)
curdoc().title = "Online Surrogate Model Strip Tool"
