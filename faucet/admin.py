__author__ = 'beast'

import click
from faucet.legacy.worker import PipeWorkerFactory, start_worker_process
from faucet.legacy.utils import get_union


@click.group()
def cli():
    pass


@click.command()
def run_workers():
    # Get Workflows from unions
    union_routes = get_union()

    workers = {}
    for route_name, route_config in union_routes.items():
        workers[route_name] = PipeWorkerFactory().build_worker(route_config, route_config["task"])


    #Start Workers
    for name, worker in workers.items():
        start_worker_process(worker)


cli.add_command(run_workers)