__author__ = 'beast'

from faucet.middleware.base import BaseMiddleware

import pickle


class PickleMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super(PickleMiddleware, self).__init__(*args, **kwargs)

        self.config = None

        if "config" in kwargs:
            self.config = kwargs["config"]


    def receive(self, env, message):
        pickled_message = pickle.loads(message)

        return self.application.receive(env, pickled_message)


    def send(self, env, message):
        pickled_message = pickle.dumps(message)

        return self.server.send(env, pickled_message)

