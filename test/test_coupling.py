from faucet import main

__author__ = 'beast'
import unittest
import os, signal,time
from multiprocessing import Process, Queue


from faucet import utils
from faucet.coupling.couplings import *

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

amqp_config = {"send":{
                               "dispatch_type" : "amqp",
                               "dsn" : "amqp://127.0.0.1:5555",
                           },
               "receive":{
                               "dispatch_type" : "amqp",
                               "dsn" : "amqp://127.0.0.1:5555",
                           },
}
class TestCouplings(unittest.TestCase):

    def setUp(self):
        pass

    def get_receive_config(self):
        utils.import_from_sibing("../other")
        import test_config

        return test_config.imap_config

    def get_send_config(self):
        utils.import_from_sibing("../other")
        import test_config

        return test_config.smtp_config




    def test_amqp_coupling(self):
        received = []

        def test_call_back(message):
            received.append(message)



        coupling = CouplingFactory().build(amqp_config, "test.amqp", "receive", test_call_back)


        p = Process(target=start_receive, args=(coupling))
        p.run()

        time.sleep(1)


        coupling = CouplingFactory().build(amqp_config, "test.amqp", "send", None)

        coupling.dispatch("test")


        time.sleep(1)

        self.assertEquals(len(received),1)

        hard_shut(p)




if __name__ == '__main__':
    unittest.main()