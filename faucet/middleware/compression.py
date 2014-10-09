__author__ = 'beast'

import logging

from faucet.middleware.base import BaseMiddleware

logger = logging.getLogger(__name__)


class GZipCompressionMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        pass


    def receive(self, env, message):
        return self.application.receive(env, message)


    def send(self, env, message):
        return self.server.send(env, message)


    def complete(self, env, message):
        return self.server.complete(env, message)


    def on_send(self, env, result):
        return self.application.on_send(env, result)

    def on_result(self, env, message):
        return self.application.on_receive(env, message)


class SnappyCompressionMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        pass


    def receive(self, env, message):
        return self.application.receive(env, message)


    def send(self, env, message):
        return self.server.send(env, message)


    def complete(self, env, message):
        return self.server.complete(env, message)


    def on_send(self, env, result):
        return self.application.on_send(env, result)

    def on_result(self, env, message):
        return self.application.on_receive(env, message)