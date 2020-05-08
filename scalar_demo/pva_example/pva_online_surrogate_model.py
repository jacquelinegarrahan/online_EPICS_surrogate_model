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


class PVServer:
    def __init__(self, pvdb):

        self.pvdb = pvdb
        self.providers = {}
        self.input_pv_state = {}

        for pvname in pvdb.keys():

            self.input_pv_state = pvdb[pvname]["value"]

            pv = SharedPV(nt=NTScalar("d"), initial=pvdb[pvname]["value"])

            @pv.put
            def onPut(pv, op):
                pv.post(op.value())
                op.done()

            self.providers[pvname] = pv

    def start_server(self):

        Server.forever(providers=[self.providers])
