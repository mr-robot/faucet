from faucet import main

__author__ = 'beast'
import unittest
from mock import MagicMock, patch
from faucet.main import MGINode, MGINodeFactory, Application, Handler, HandlerFactory
from faucet.middleware import BaseMiddleware, SimpleLoggingMiddleware, GraphiteMiddleware


class TestMiddleware(unittest.TestCase):
    def setUp(self):
        self.test_union = {"test": {"receive": {
            "dispatch_type": "test", },
                                    "handler": Handler

        }}


    def test_base_create(self):
        mock_node = MagicMock(spec=MGINode)
        mock_application = MagicMock(spec=Application)

        env = {"env": "dict", "uri": "test"}
        message = "Response Message"

        base_middleware = BaseMiddleware(application=mock_application)
        base_middleware.register_server(mock_node)

        base_middleware.receive(env, message)
        base_middleware.send(env, message)

        mock_node.send.assert_called_with(env, message)

        mock_application.receive.assert_called_with(env, message)


    def test_graphite_create(self):
        mock_node = MagicMock(spec=MGINode)
        mock_application = MagicMock(spec=Application)

        env = {"env": "dict", "uri": "test", }
        message = "Response Message"
        config = {"graphite_server": "localhost", "graphite_port": 2003, "dryrun": True}

        base_middleware = GraphiteMiddleware(application=mock_application, config=config)
        base_middleware.register_server(mock_node)

        base_middleware.receive(env, message)
        base_middleware.send(env, message)

        mock_node.send.assert_called_with(env, message)

        mock_application.receive.assert_called_with(env, message)


if __name__ == '__main__':
    unittest.main()