__author__ = 'beast'
import unittest

from faucet.main import MGINode, Application, Handler, HandlerFactory


class TestApplication(unittest.TestCase):
    def setUp(self):
        self.test_union = {"test": {"receive": {
            "dispatch_type": "test", },
                                    "handler": Handler

        }}


    def test_basic_create(self):
        mock_node = MagicMock(spec=MGINode)

        application = Application(union=self.test_union)

        self.assertIsNotNone(application)

        application.register_server(mock_node)

        self.assertEquals(application.server, mock_node)


    def test_basic_send(self):
        mock_node = MagicMock(spec=MGINode)

        application = Application(union=self.test_union)

        self.assertIsNotNone(application)

        application.register_server(mock_node)

        return_value = ({"env": "dict", "uri": "test"}, "Response Message")

        mock_handler = MagicMock()


        # Receive


        handler = application.get_handler_for_uri("test")

        handler.send(return_value[0], return_value[1])

        mock_node.send.assert_called_with(return_value[0], return_value[1])


    def test_basic_receive(self):
        return_value = ({"env": "dict", "uri": "test"}, "Response Message")

        mock_handler = MagicMock(spec=Handler)
        mock_node = MagicMock(spec=MGINode)
        mock_factory = MagicMock(spec=HandlerFactory)
        mock_factory.get_handler.return_value = mock_handler

        application = Application(union=self.test_union, handler_factory=mock_factory)

        self.assertIsNotNone(application)

        application.register_server(mock_node)

        application.receive(return_value[0], return_value[1])

        mock_handler.receive.assert_called_with(return_value[0], return_value[1])


if __name__ == '__main__':
    unittest.main()