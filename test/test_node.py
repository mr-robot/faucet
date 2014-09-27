from faucet import main

__author__ = 'beast'
import unittest
from mock import MagicMock, patch
import os, signal,time
from multiprocessing import Process, Queue


from faucet import utils
from faucet.main import MGINode, MGINodeFactory, Application
from faucet.coupling.couplings import CouplingFactory, Coupling

class TestNode(unittest.TestCase):

    def setUp(self):
        pass


    def test_basic_create(self):
        magic_mock = MagicMock()

        node = MGINodeFactory().build(magic_mock, {"uri":"test"})

        self.assertIsNotNone(node)

        magic_mock.register_server.assert_called_with(node)


        self.assertIsNotNone(node.manager)

        self.assertEquals(node.application, magic_mock)


    def test_basic_receive(self):
        mock_application = MagicMock(spec=Application)
        mock_coupling = MagicMock(spec=Coupling)

        return_value = ({"env":"dict"},"Response Message")
        mock_coupling.receive.return_value = return_value

        mock_cf = MagicMock(spec=CouplingFactory)
        mock_cf.build.return_value = mock_coupling


        node = MGINodeFactory().build(mock_application, {"test":{"receive":{
                                                                 "dispatch_type":"test"}}}, mock_cf)

        self.assertIsNotNone(node)

        mock_application.register_server.assert_called_with(node)

        mock_handler = MagicMock()


        #Receive

        node.receive( {"uri":"test"})

        mock_coupling.receive.assert_called()

        mock_cf.build.assert_called()

        mock_application.receive.assert_called()
        mock_application.receive.assert_called_with(return_value[0], return_value[1])



    def test_basic_send(self):
        mock_application = MagicMock(spec=Application)
        mock_coupling = MagicMock(spec=Coupling)

        return_value = ({"env":"dict"},"Response Message")
        send_message = "Send Message"

        mock_coupling.dispatch.return_value = return_value

        mock_cf = MagicMock(spec=CouplingFactory)
        mock_cf.build.return_value = mock_coupling


        node = MGINodeFactory().build(mock_application, {"test":{"send":{
                                                                 "dispatch_type":"test"}}}, mock_cf)

        self.assertIsNotNone(node)

        mock_application.register_server.assert_called_with(node)

        mock_handler = MagicMock()


        #Receive

        node.send( {"uri":"test"}, send_message)

        mock_coupling.dispatch.assert_called()

        mock_cf.build.assert_called()

        print mock_application.mock_calls

        mock_application.on_send.assert_called_with(return_value[0], return_value[1])

if __name__ == '__main__':
    unittest.main()