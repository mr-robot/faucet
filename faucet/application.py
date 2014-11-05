__author__ = 'mr-robot'

from faucet.coupling.couplings import CouplingFactory
from faucet.middleware import AbstractMiddlewareFactory

from faucet.node import MGINode
from faucet.handler import HandlerFactory


class Application(object):
    def __init__(self, *args, **kwargs):
        self.union = kwargs["union"]

        if "handler_factory" in kwargs:
            self.handler_factory = kwargs["handler_factory"]
        else:
            self.handler_factory = HandlerFactory(self.union)

    def register_server(self, server):
        self.server = server


    def get_handler_for_uri(self, uri):


        return self.handler_factory.get_handler(self, uri)

    def request_receive(self, uri, handler):

        self.server.receive(uri, handler)


    def receive(self, env, message):
        # Get Handler from union
        handler = self.get_handler_for_uri(env["uri"])
        # Route to Handler
        return handler.receive(env, message)

    def send(self, env, message):
        # Route it from Handler
        return self.server.send(env, message)

    def on_send(self, env, send_result):
        pass

    def complete(self, env, message):


        return self.server.complete(env["uri"], message)




def send(handler_uri, union, env, message):
    application = Application(union)

    server = MGINode(application)

    handler = application.get_handler_for_uri(handler_uri)

    return handler.send(env, message)


class MGINodeFactory(object):
    def build(self, application, union, coupling_factory=None):
        return MGINode(application=application, union=union, coupling_factory=coupling_factory)


class FullStackBuilder(object):
    def build(self, application, union, middleware_factory=AbstractMiddlewareFactory(), node_factory=MGINodeFactory()):
        parent_application = application
        for middleware_config_child, config in union["middleware"].items():
            parent_application = middleware_factory.build_middleware(config, parent_application)

        return node_factory.build(parent_application, union)


