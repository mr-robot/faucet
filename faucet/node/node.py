__author__ = 'beast'

from faucet.coupling.couplings import CouplingFactory

class Manager(object):
    def __init__(self, *args, **kwargs):
        self.union = kwargs["union"]
        self.coupling_factory = kwargs["coupling_factory"]
        self.couplings = {}

    def get_coupling(self, env, role):
        uri = env["uri"]
        coupling_config = self.union[uri]

        if not (uri in self.couplings):
            self.couplings[uri] = self.coupling_factory.build(coupling_config, uri, role)

        return self.couplings[uri]

    def send(self, env, message, on_send):
        return self.get_coupling(env, "send").dispatch(message, on_send)


    def receive(self, env, on_receive):
        return self.get_coupling(env, "receive").receive(on_receive)

    def complete(self, uri, message):
        return self.get_coupling(uri, "receive").complete(message)


class MGINode(object):
    def __init__(self, *args, **kwargs):
        self.application = kwargs["application"]
        self.union = kwargs["union"]

        c_f = CouplingFactory()

        if "coupling_factory" in kwargs and kwargs["coupling_factory"]:
            c_f = kwargs["coupling_factory"]

        self.application.register_server(self)
        self.manager = Manager(union=self.union, coupling_factory=c_f)


    def send(self, env, message):
        response = self.manager.send(env, message, self.on_send)

        if response:
            send_env, send_response = response
            self.on_send(send_env, send_response)

    def on_send(self, env, response):

        self.application.on_send(env, response)


    def receive(self, env):


        response = self.manager.receive(env, self.on_receive)

        if response:
            env, message = response

            self.on_receive(env, message)


    def on_receive(self, env, message):


        self.application.receive(env, message)


    def complete(self, env, message):
        return self.manager.complete(env, message)

    def run(self, uri):

        while (True):
            self.receive(uri)
