import logging
import signal
import sys
import uuid
from multiprocessing import Process

import os
from luigi import scheduler, worker
from faucet.main import MGINode, Application, FullStackBuilder


def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    sys.exit(0)


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class PipeWorker(object):
    def __init__(self, config, role, task_string):

        self.worker_id = unicode(uuid.uuid4())
        self.configure_messaging(config, role)

        self.setup_working_path()

        self.setup_destination(config)

        self.task = load_class(task_string)

        signal.signal(signal.SIGTERM, sigterm_handler)

    def configure_messaging(self, config, role):
        self.pipe = ReceivePipe(config)

        return self.pipe

    def setup_working_path(self):
        self.working_path = os.path.join(os.getcwd(), "tmp", self.worker_id)

        if not os.path.exists(self.working_path):
            os.makedirs(self.working_path)

    def setup_destination(self, config):
        self.destination = config["destination"]

    def save_to_path(self, message):
        message_path = get_working_path(self.working_path, message.uuid)

        message.path = message_path

        with open(message_path, "w") as message_file:
            message_file.write(message.original_message_contents)

        message.path = message_path

        return message


    def run(self):
        logging.info("Starting Worker")
        try:
            while (True):
                # Receive From Network adapters
                for message in self.pipe.receive():

                    logging.info("Received Message")

                    message = self.save_to_path(message)

                    if self.execute(message):
                        self.pipe.complete(message)
        finally:
            logging.info("Shutting down Worker")


    def execute(self, message):
        if self.task:
            task = self.task(message=message, working_path=self.working_path, destination=self.destination)
            sch = scheduler.CentralPlannerScheduler()
            w = worker.Worker(scheduler=sch)
            w.add(task)
            w.run()

            return True


class NodeWorker(object):

    def __init__(self, input_union, uri, coupling_factory=None):

        self.worker_id = unicode(uuid.uuid4())

        self.input_union = input_union
        self.uri = uri


    def build(self, input_union):
        app = Application(union=input_union)


        server = MGINode(application=app, union=input_union)

        return server


    def run(self):

        logging.info("Starting Worker")

        server = self.build(self.input_union)
        try:
            while (True):
                # Receive From Network adapters

                server.run(self.uri)
        finally:
            logging.info("Shutting down Worker")

def run_worker(worker_obj):
    worker_obj.run()


def start_worker_process(worker_obj):
    p = Process(target=run_worker, kwargs={"worker_obj": worker_obj})
    p.start()
    p.join()


class NodeWorkerFactory(object):
    def build_worker(self, config, task, role="receive"):
        return NodeWorker(config, role, task)
