__author__ = 'beast'

import click
from worker import start_worker_process, NodeWorker, NodeWorkerFactory
from utils import get_union

@click.group()
def cli():
    pass


@click.command()
def run_nodes():
    # Get Workflows from unions
    union_routes = get_union()

    workers = {}
    for route_name, route_config in union_routes.items():
        workers[route_name] = NodeWorkerFactory().build_worker(route_config, route_config["task"])


    # Start Workers
    for name, worker in workers.items():
        start_worker_process(worker)

@click.command()
def validate_config():
    # Get Workflows from unions

    union_routes = get_union()

    pass

cli.add_command(validate_config)
cli.add_command(run_nodes)