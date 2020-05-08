# from matrix_tracker import lattice
import copy
import multiprocessing
from pcaspy import Driver, SimpleServer
import time
from epics import caget, PV
import numpy as np
import random
from MakeModel import SurrogateModel

from p4p.nt import NTScalar
from p4p.server.thread import SharedPV
from p4p.server import Server
from p4p.server.thread import Handler


class MyHandler:
    def put(self, op):
        pass

    def rpc(self, op):
        pass

    def onFirstConnect(self):  # may be omitted
        pass

    def onLastDisconnect(self):  # may be omitted
        pass


class PVServer:
    def __init__(self, pvdb):

        self.pvdb = pvdb
        self.providers = {}
        self.input_pv_state = {}

        for pvname in pvdb.keys():

            self.input_pv_state = pvdb[pvname]["value"]

            pv = SharedPV(handler=CMDPVHandler())  # SharedPV(nt=NTScalar('d'),initial=pvdb[pvname]['value'])

            @pv.put
            def onPut(pv, op):
                pv.post(op.value())  # just store and update subscribers
                pvname = op.name()
                v = op.value()

                op.done()

            self.providers[pvname] = pv

    def start_server(self):

        Server.forever(providers=[self.providers])


if __name__ == "__main__":

    pv = SharedPV(MyHandler())

    sm = SurrogateModel(model_file="model_weights.h5")

    cmd_pvdb = {}
    for ii, input_name in enumerate(sm.input_names):
        cmd_pvdb[input_name] = {"type": "d", "value": sm.input_ranges[ii][0]}

    sim_pvdb = {}
    for ii, output_name in enumerate(sm.output_names):
        sim_pvdb[output_name] = {"type": "d", "value": 0}

    server = PVServer(cmd_pvdb)
    server.start_server()
