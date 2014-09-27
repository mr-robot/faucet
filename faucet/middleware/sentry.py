__author__ = 'beast'

import logging


from faucet.middleware.base import BaseMiddleware

logger = logging.getLogger(__name__)


from raven.handlers.logging import SentryHandler

from raven.conf import setup_logging




class SentryMiddleware(BaseMiddleware):

    def __init__(self, *args, **kwargs):


        handler = SentryHandler('http://public:secret@example.com/1')

        setup_logging(handler)


    def receive(self, env, message):

        return self.application.receive(env, message)


    def send(self, env, message):

        return self.server.send(env, message)


    def complete(self, env, message):
        return self.server.complete(env, message)


