import numpy as np
import time

from p4p.client.thread import Context
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.layouts import column, row

from scalar_demo import PREFIX

CONTEXT = Context("pva")

class pv_buffer:
    def __init__(self, pv, buffer_size):

        self.pvname = pv
        self.tstart = time.time()
        self.time = np.array([self.tstart])
        self.buffer_size = buffer_size
        self.data = np.array([0.0])

    def poll(self):
        
        t = time.time()
        v = CONTEXT.get(self.pvname)

        self.time = np.append(self.time, t)
        self.data = np.append(self.data, v)

        return self.time - self.tstart, self.data


pvbuffer = pv_buffer(f"{PREFIX}:x_95coremit", 100)
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
