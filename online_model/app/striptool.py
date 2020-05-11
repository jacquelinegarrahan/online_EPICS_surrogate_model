import numpy as np
import time
from argparse import ArgumentParser
from epics import caget, caput, PV
from p4p.client.thread import Context
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.layouts import column, row

from scalar_demo import PREFIX

# Parse arguments passed through bokeh serve
# requires protocol to be set
parser = ArgumentParser()
parser.add_argument("-p", "--protocol", metavar="PROTOCOL", nargs=1, type=str, choices=["pva", "ca"], help='Protocol to use (ca, pva)', required=True)
args = parser.parse_args()

PROTOCOL = args.protocol[0]

# initialize context for pva
CONTEXT = None
if PROTOCOL == "pva":
    CONTEXT = Context("pva")


class pv_buffer:
    def __init__(self, pv, buffer_size):

        self.pvname = pv

        #initialize data and time depending on protocol
        # TODO: Check monitors for pva as an alternative to raw polling
        if PROTOCOL == "ca":
            self.pv = PV(pv, auto_monitor=True) 
            self.data = np.array([caget(self.pvname)])

        elif PROTOCOL == "pva":
            self.data = np.array([CONTEXT.get(self.pvname)])

        self.tstart = time.time()
        self.time = np.array([self.tstart])

        self.buffer_size = buffer_size

    def poll(self):
        t = time.time()

        if PROTOCOL == "ca":
            v = caget(self.pvname)

            if len(self.data) < self.buffer_size:
                self.time = np.append(self.time, t)
                self.data = np.append(self.data, v)

            else:
                self.time[:-1] = self.time[1:]
                self.time[-1] = t
                self.data[:-1] = self.data[1:]
                self.data[-1] = v

        elif PROTOCOL == "pva":
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
