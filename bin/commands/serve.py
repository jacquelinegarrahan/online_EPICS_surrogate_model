import click
import os


@click.group()
def serve():
    pass


@scrape.command()
def launch_ca_server(server):
    from scalar_demo.ca_example.MakeModel import SurrogateModel
    from scalar_demo.ca_example.online_surrogate_model import SyncedSimPVServer

    sm = SurrogateModel(model_file="model_weights.h5")

    cmd_pvdb = {}
    for ii, input_name in enumerate(sm.input_names):
        cmd_pvdb[input_name] = {"type": "float", "prec": 8, "value": sm.input_ranges[ii][0]}

    sim_pvdb = {}
    for ii, output_name in enumerate(sm.output_names):
        sim_pvdb[output_name] = {"type": "float", "prec": 8, "value": 0}

    # Add in noise for fun
    sim_pvdb["x_95coremit"]["scan"] = 0.2
    noise_params = {"x_95coremit": {"sigma": 0.5e-7, "dist": "uniform"}}
    # noise_params=None

    server = SyncedSimPVServer("smvm", cmd_pvdb, sim_pvdb, noise_params, sm)
    server.start_server()


@scrape.command()
def launch_pva_server(server):
    from scalar_demo.pva_example.MakeModel import SurrogateModel
    from scalar_demo.pva_example.online_surrogate_model import SyncedSimPVServer

    sm = SurrogateModel(model_file="model_weights.h5")

    cmd_pvdb = {}
    for ii, input_name in enumerate(sm.input_names):
        cmd_pvdb[input_name] = {"type": "d", "value": sm.input_ranges[ii][0]}

    sim_pvdb = {}
    for ii, output_name in enumerate(sm.output_names):
        sim_pvdb[output_name] = {"type": "d", "value": 0}

    server = PVServer(cmd_pvdb)
    server.start_server()
