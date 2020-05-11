import click
import os

MODEL_FILE = "online_model/model/model_weights.h5"


@click.group()
def serve():
    pass



@serve.command()
@click.argument('protocol')
def start_server(protocol):
    """
    Start server using given PROTOCOL.

    PROTOCOL options are 'ca' and 'pva'
    """

    from online_model.model.surrogate_model import SurrogateModel
    sm = SurrogateModel(model_file=MODEL_FILE)

    # set up process variable databases
    cmd_pvdb = {}
    for ii, input_name in enumerate(sm.input_names):
        cmd_pvdb[input_name] = {"type": "float", "prec": 8, "value": sm.input_ranges[ii][0]}

    sim_pvdb = {}
    for ii, output_name in enumerate(sm.output_names):
        sim_pvdb[output_name] = {"type": "float", "prec": 8, "value": 0}


    if protocol == "ca":
        from online_model.server.ca import SyncedSimPVServer

        # Add in noise
        sim_pvdb["x_95coremit"]["scan"] = 0.2
        noise_params = {"x_95coremit": {"sigma": 0.5e-7, "dist": "uniform"}}

        server = SyncedSimPVServer(cmd_pvdb, sim_pvdb, noise_params, sm)
        server.start_server()
            

    elif protocol == "pva":
        from online_model.server.pva import PVAServer

        server = PVAServer(cmd_pvdb, sim_pvdb, sm)
        server.start_server()

    else:
        print("Given protocol %s is not supported.", protocol)
