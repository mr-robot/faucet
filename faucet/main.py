__author__ = 'mr-robot'

from coupling.couplings import CouplingFactory

class Manager(object):

    def __init__(self, *args, **kwargs):
        self.union = kwargs["union"]
        self.coupling_factory = kwargs["coupling_factory"]
        self.couplings = {}

    def get_coupling(self, env, role):
        uri = env["uri"]
        coupling_config = self.union[uri]

        if not (uri in self.couplings):

            self.couplings[uri] = self.coupling_factory.build(coupling_config, uri ,role)

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
        response = self.manager.send(env,message,self.on_send)

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
        return self.manager.complete(env,message)

    def run(self, uri):

        while(True):
            self.receive(uri)


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
        #Get Handler from union
        handler = self.get_handler_for_uri(env["uri"])
        #Route to Handler
        return handler.receive(env, message)

    def send(self, env, message):
        #Route it from Handler
        return self.server.send(env, message)

    def on_send(self, env, send_result):
        pass

    def complete(self, env, message):


        return self.server.complete(env["uri"], message)


class HandlerFactory(object):

    def __init__(self, union):
        self.union = union

    def get_handler(self, application,  uri):

        env = {}
        env["uri"] = uri
        env["application"] = application
        return self.union[uri]["handler"](**env)


class Handler(object):

    def __init__(self, *args, **kwargs):

        self.application = kwargs["application"]
        self.uri = kwargs['uri']



    def dispatch(self, env, message):
        #To Send we need to get an Application object
        return self.application.send(env, message)



    def receive(self, env, message):
        return None

    def send(self, env, message):
        return self.dispatch(env, message)

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
