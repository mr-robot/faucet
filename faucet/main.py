__author__ = 'mr-robot'

from coupling.couplings import CouplingFactory

class Manager(object):

    def __init__(self, *args, **kwargs):
        self.union = kwargs["union"]
        self.coupling_factory = kwargs["coupling_factory"]
        self.couplings = {}

    def get_coupling(self, uri, role):
        coupling_config = self.union[uri]

        if not (uri in self.couplings):

            self.couplings[uri] = self.coupling_factory.build(coupling_config, uri ,role, self.on_receive)

        return self.couplings[uri]

    def send(self, uri, message):

        return self.get_coupling(uri, "send").dispatch(message)

    def on_receive(self, uri, message):
        return self.node.on_receive(uri, message)

    def receive(self, uri):


        return self.get_coupling(uri, "receive").receive()

    def complete(self, uri, message):

        return self.get_coupling(uri, "receive").complete(message)

class MGINode(object):

    def __init__(self, *args, **kwargs):
        self.application = kwargs["application"]
        self.union = kwargs["union"]

        c_f = CouplingFactory()

        if "coupling_factory" in kwargs:
            c_f = kwargs["coupling_factory"]

        self.application.register_server(self)
        self.manager = Manager(union=self.union, coupling_factory=c_f)


    def send(self, uri, message):
        return self.manager.send(uri,message)


    def receive(self, uri, handler=None, message=None):

        if message:
            self.application.receive({}, message, handler)

        response = self.manager.receive(uri)

        if response:

            env, message = response

            self.application.receive(env, message, handler)




    def complete(self, env, message):
        return self.manager.complete(env,message)

    def run(self, uri):

        while(True):
            self.receive(uri)


class Application(object):

    def __init__(self, *args, **kwargs):
        self.union = kwargs["union"]

    def register_server(self, server):
        self.server = server


    def get_handler_for_uri(self, uri):



        return self.union[uri]["handler"]

    def request_receive(self, uri, handler):

        self.server.receive(uri, handler)


    def receive(self, env, message, handler):
        #Get Handler from union
        if not handler:
            handler = self.get_handler_for_uri(env["uri"])
        #Route to Handler

            env["application"] = self

            return handler(**env).receive(message)
        else:
            return handler.receive(message)


    def send(self, env, message):
        #Route it from Handler
        return self.server.send(env["uri"], message)

    def complete(self, env, message):


        return self.server.complete(env["uri"], message)



class Handler(object):

    def __init__(self, *args, **kwargs):

        self.application = kwargs["application"]
        self.uri = kwargs['uri']



    def dispatch(self, env, message):
        #To Send we need to get an Application object
        return self.application.send(env, message)

    def request_receive(self):
        return self.application.request_receive(self.uri, self)


    def receive(self, message):
        return None

    def send(self, *args, **kwargs):
        yield self.dispatch(None)

    def complete(self, message):
        return self.application.complete(message)


def send(handler_uri, *args, **kwargs):


    application = Application(*args, **kwargs)

    server = MGINode(application)

    kwargs["uri"] = handler_uri

    handler = application.get_handler_for_uri(handler_uri)(*args, **kwargs)

    return handler.send(*args, **kwargs)


