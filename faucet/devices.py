__author__ = 'ClephaTi'

import zmq, logging


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def main():
    try:
        context = zmq.Context(1)

        frontend = context.socket(zmq.PULL)
        frontend.bind('tcp://*:5559')
        # frontend.setsockopt(zmq.PULL, '')

        backend = context.socket(zmq.PUSH)
        backend.bind('tcp://*:5560')

        print 'starting zmq forwarder'
        zmq.device(zmq.FORWARDER, frontend, backend)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception(e)
    finally:
        frontend.close()
        backend.close()
        context.term()


def router_dealer_proxy():
    """ main method """

    context = zmq.Context()

    # Socket facing clients
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5555")

    # Socket facing services
    backend = context.socket(zmq.DEALER)
    backend.bind("tcp://*:5560")

    print 'starting zmq proxy'
    zmq.device(zmq.QUEUE, frontend, backend)

    # We never get here
    frontend.close()
    backend.close()
    context.term()


if __name__ == '__main__':
    router_dealer_proxy()
