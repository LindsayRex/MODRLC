# Simulation of the model
import sys
import requests
import urllib3

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'interfaces' / 'dompc'))
from actb_simulator.actb_simulator import ActbSimulator
from template_model import ModelParameters

sys.path.insert(0, str(Path(__file__).parent.absolute().parent.parent.parent / 'actb_client'))
from actb_client import ActbClient


def template_simulator(model):
    # Check if BOPTEST is up and running, if not, then default to just using the state-space
    # equations.

    mp = ModelParameters()
    try:
        client = ActbClient(url='http://127.0.0.1:80')
        client.stop_all()
        client.select('spawnrefsmalloffice')
        if client.name() is not None:
            print("ACTB is configured to act as simulator")
            client.set_step(step=mp.time_step)
            client.initialize(start_time=mp.start_time)
        else:
            print("Defaulting to simulator=model")
            client = None
    except (requests.exceptions.ConnectionError, urllib3.exceptions.NewConnectionError,):
        print("ACTB is not running, if desired launch ACTB using `make run`")
        print("Will continue in simulator=model mode")
        client = None

    if client is not None:
        simulator = ActbSimulator(model, client)
    else:
        simulator = ActbSimulator(model)

    # We are running the MPC model at t=300 seconds (5 min).
    simulator.set_param(t_step=mp.time_step)

    mp.tvp_template_simulator = simulator.get_tvp_template()
    simulator.set_tvp_fun(mp.tvp_fun_simulator)

    simulator.setup()

    return simulator, client
