__author__ = 'mr-robot'


class HandlerFactory(object):
    def __init__(self, union):
        self.union = union

    def get_handler(self, application, uri):
        env = {}
        env["uri"] = uri
        env["application"] = application
        return self.union[uri]["handler"](**env)


class Handler(object):
    def __init__(self, *args, **kwargs):
        self.application = kwargs["application"]
        self.uri = kwargs['uri']


    def dispatch(self, env, message):
        # To Send we need to get an Application object
        return self.application.send(env, message)


    def receive(self, env, message):
        return None

    def send(self, env, message):
        self.dispatch(env, message)

    def complete(self, env, message):
        return self.application.complete(message)
