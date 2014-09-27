__author__ = 'beast'


from faucet.utils import module_exists, ConfigStruct, load_class

from base import SimpleLoggingMiddleware
from sentry import SentryMiddleware
from graphite import GraphiteMiddleware



class DictionaryMiddlewareFactory(object):

    def get_middleware(self, config, application):

        if "class" in config:
            return load_class(config["class"])(application=application)
        else:
            if "name" in config:
                return self.get_built_in(config["name"], application)

    def get_built_in(self, name, application):
        if name == "simple":
            return SimpleLoggingMiddleware(application)
        elif name == "graphite":
            return SimpleLoggingMiddleware(application)
        elif name == "sentry":
            return SimpleLoggingMiddleware(application)

class AbstractMiddlewareFactory(object):

    def __init__(self, factory=DictionaryMiddlewareFactory()):
        self.factory = factory

    def build_middleware(self, config, application):
        return self.factory.get_middleware(config, application)