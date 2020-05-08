# from matrix_tracker import lattice
import copy
import multiprocessing
from pcaspy import Driver, SimpleServer
import time
from epics import caget, PV
import numpy as np
import random

from p4p.nt import NTScalar
from p4p.server.thread import SharedPV
from p4p.server import Server
from p4p.client.thread import Context
from p4p.rpc import rpc, quickRPCServer


CONTEXT = Context("pva")

class PVAServer:
    def __init__(self, in_pvdb, out_pvdb, model):

        self.in_pvdb = in_pvdb
        self.out_pvdb = out_pvdb
        self.providers = {}
        self.input_pv_state = {}
        self.output_pv_state = {}

        # create PVs for model inputs
        for pvname in in_pvdb:

            self.input_pv_state = in_pvdb[pvname]["value"]

            pv = SharedPV(nt=NTScalar("d"), initial=in_pvdb[pvname]["value"])

            # put handlers receive callbacks with put operation requested
            @pv.put
            def onPut(pv, op):
                pv.post(op.value())
                # run model
                print("Updated value: %s - %s", op.name(), op.value())
                self.output_pv_state = self.model.run(self.input_pv_state, verbose=True)
                # do we want this to be blocking?? 
                self.set_output_pvs(output_pv_state)
                op.done()

            self.providers[pvname] = pv

        # create PVs for model outputs
        for pvname in out_pvdb:
            self.input_pv_state = out_pvdb[pvname]["value"]

            pv = SharedPV(nt=NTScalar("d"), initial=out_pvdb[pvname]["value"])

            # put handlers receive callbacks with put operation requested
            @pv.put
            def onPut(pv, op):
                pv.post(op.value())
                # run model
                print("Ouput value: %s - %s", op.name(), op.value())
                op.done()

            self.providers[pvname] = pv


    def set_output_pvs(self, output_pvs):
        for pvame, value in self.output_pv_state:
            providers[pvname].put(value)

    def start_server(self):
        # no need to poll
        prefix = "test_prefix"
        Server.forever(providers=[self.providers])


