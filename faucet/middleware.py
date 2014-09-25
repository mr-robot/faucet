__author__ = 'beast'

import logging

class BaseMiddleware(object):


    def __init__(self, *args, **kwargs):
        self.application = kwargs["application"]

        self.application.register_server(self)

    def register_server(self, server):
        self.server = server

    def receive(self, env, message):
        return self.application.receive(env, message)

    def send(self, env, message):
        #Route it from Handler
        return self.server.send(env, message)

    def on_send(self, env, send_result):
        pass

    def complete(self, env, message):
        return self.server.complete(env, message)


class SimpleLoggingMiddleware(BaseMiddleware):

    def receive(self, env, message):

        return self.application.receive(env, message)


    def send(self, env, message):

        return self.server.send(env, message)


    def complete(self, env, message):
        return self.server.complete(env, message)

