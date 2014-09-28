__author__ = 'beast'

from faucet.middleware.base import BaseMiddleware

import graphitesend


class GraphiteMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):

        super(GraphiteMiddleware, self).__init__(*args, **kwargs)

        self.config = None

        if "config" in kwargs:
            self.config = kwargs["config"]


    def get_graphite(self, uri, system_name):
        if self.config:
            return graphitesend.init(fqdn_squash=True, system_name=system_name, prefix=uri,
                                     graphite_server=self.config["graphite_server"],
                                     graphite_port=self.config["graphite_port"], dryrun=self.config["dryrun"])
        else:
            return graphitesend.init(fqdn_squash=True, system_name=system_name, prefix=uri)


    def receive(self, env, message):

        self.get_graphite(env["uri"], "receive").send("count", 1)

        return self.application.receive(env, message)


    def send(self, env, message):

        self.get_graphite(env["uri"], "send").send("count", 1)

        return self.server.send(env, message)


    def complete(self, env, message):

        self.get_graphite(env["uri"], "complete").send("count", 1)

        return self.server.complete(env, message)


