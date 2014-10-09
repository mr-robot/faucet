__author__ = 'beast'

import os
import signal

from faucet import utils
from faucet.coupling.couplings import Coupling


class TestCoupling():
    def __init__(self, env):
        self.env = env
        self.handler_list = []

    def receive(self, message):
        self.handler_list.append(message)
        return True

    def send(self, message):
        self.handler_list.append(message)
        return True


class MockCoupling(Coupling):
    def receive(self, uri):
        return {"uri": uri}, None


class MockCouplingFactory(object):
    def build(self, config, role):
        return MockCoupling(utils.ConfigStruct(**config[role]), role)


def hard_shut(p):
    os.killpg(p.pid, signal.SIGTERM)


def start_receive(coupling):
    coupling.receive()


amqp_config = {"send": {
    "dispatch_type": "amqp",
    "dsn": "amqp://127.0.0.1:5555",
},
               "receive": {
                   "dispatch_type": "amqp",
                   "dsn": "amqp://127.0.0.1:5555",
               },
}