import random

from p4p.nt import NTScalar
from p4p.server.thread import SharedPV
from p4p.server import Server

from scalar_demo.model.surrogate_model import SurrogateModel
from scalar_demo import PREFIX, MODEL_FILE


providers = {}
model = SurrogateModel(model_file = MODEL_FILE)

class InputHandler:

    def put(self, pv, op):
        global providers
        global model

        pv.post(op.value())
        input_pvs[op.name().replace(f"{PREFIX}:", "")] = op.value()
        output_pv_state = model.run(input_pvs, verbose=True)

        # now update output variables
        for pv_item, value in output_pv_state.items():
            output_provider = providers[f"{PREFIX}:{pv_item}"]
            output_provider.post(value[0])

        # mark server operation as complete
        op.done()

    def rpc(self, pv, op):
        pass


class PVAServer:
    def __init__(self, in_pvdb, out_pvdb, model):

        global providers

        self.in_pvdb = in_pvdb
        self.out_pvdb = out_pvdb

        #initialize model and state
        input_pvs = {}
        for in_pv in in_pvdb:
            input_pvs[in_pv] = in_pvdb[in_pv]["value"]

        model.run(input_pvs, verbose=True)

        # create PVs for model inputs
        for in_pv in in_pvdb:
            pvname = f"{PREFIX}:{in_pv}"
            pv = SharedPV(handler=InputHandler(), nt=NTScalar("d"), initial=in_pvdb[in_pv]["value"])
            providers[pvname] = pv

        # create PVs for model outputs
        for out_pv in out_pvdb:
            pvname = f"{PREFIX}:{out_pv}"

            # use default handler for the output process variables 
            # updates are handled from post calls within the input update processing 
            pv = SharedPV(nt=NTScalar("d"), initial=out_pvdb[out_pv]["value"])
            providers[pvname] = pv

    def start_server(self):
        Server.forever(providers=[providers])