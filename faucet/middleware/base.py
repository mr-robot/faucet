__author__ = 'beast'

__author__ = 'beast'

import logging

logger = logging.getLogger(__name__)


class BaseMiddleware(object):
    def __init__(self, *args, **kwargs):
        self.application = kwargs["application"]

        self.application.register_server(self)

    def register_server(self, server):
        self.server = server

    def receive(self, env, message):
        return self.application.receive(env, message)

    def send(self, env, message):
        # Route it from Handler
        return self.server.send(env, message)


    def on_send(self, env, result):
        return self.application.on_send(env, result)

    def on_result(self, env, message):
        return self.application.on_receive(env, message)

    def complete(self, env, message):
        return self.server.complete(env, message)


class SimpleLoggingMiddleware(BaseMiddleware):
    def receive(self, env, message):
        return self.application.receive(env, message)


    def send(self, env, message):
        return self.server.send(env, message)


    def complete(self, env, message):
        return self.server.complete(env, message)


