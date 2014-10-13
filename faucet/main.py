__author__ = 'mr-robot'

from coupling.couplings import CouplingFactory
from middleware import AbstractMiddlewareFactory

from faucet.node import MGINode


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


class HandlerFactory(object):
    def __init__(self, union):
        self.union = union

    def get_handler(self, application, uri):
        env = {}
        env["uri"] = uri
        env["application"] = application
        return self.union[uri]["handler"](**env)


class Handler(object):
    def __init__(self, *args, **kwargs):
        self.application = kwargs["application"]
        self.uri = kwargs['uri']


    def dispatch(self, env, message):
        # To Send we need to get an Application object
        return self.application.send(env, message)


    def receive(self, env, message):
        return None

    def send(self, env, message):
        self.dispatch(env, message)

    def complete(self, env, message):
        return self.application.complete(message)


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


