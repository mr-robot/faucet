from faucet.coupling.beanstalk import BeanStalkCoupling

__author__ = 'mr-robot'

import logging
import urlparse

from faucet.utils import module_exists, ConfigStruct
from faucet.message import Message


SEND_ROLE = "send"
RECEIVE_ROLE = "receive"
ROLES = [SEND_ROLE, RECEIVE_ROLE]

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

if module_exists("pika"):
    import pika

if module_exists("kafka"):
    import kafka

if module_exists("redis"):
    from redis import Redis

if module_exists("rq"):
    from rq import Queue

if module_exists("envelopes"):
    logging.info("Importing Envelopes Lib")
    import envelopes

if module_exists("zmq"):
    import zmq
    from zmq.eventloop.zmqstream import ZMQStream
    from zmq.eventloop import ioloop

if module_exists("nsq"):


def work_container(message):
    pass


class DispatchConfig(object):
    def __init__(self, method, *args, **kwargs):
        self.method = method


class Coupling(object):
    def __init__(self, config, uri, role):
        self.config = {"raw": config}
        self.role = role
        self.uri = uri

        self.io_loop = None

        self.process_config(config)

    def process_config(self, config):

        if hasattr(config, "dsn"):
            result = urlparse.urlparse(config.dsn)

            self.port = result.port
            self.hostname = result.hostname
            self.username = result.username
            self.password = result.password
            self.fragment = result.fragment

        if "username" in config.__dict__:
            self.username = config.username

        if "password" in config.__dict__:
            self.password = config.password

        if "hostname" in config.__dict__:
            self.hostname = config.hostname

        if "timeout" in config.__dict__:
            self.timeout = config.timeout

        if "queue" in config.__dict__:
            self.queue = config.queue

        if "io_loop" in config.__dict__:
            self.io_loop = config.io_loop


    def build(self):
        pass

    def dispatch(self, message, on_send=None):
        pass

    def receive(self, uri, on_receive):
        pass

    def complete(self):
        pass

    def name(self):
        return self.__class__.__name__


class RQCoupling(Coupling):
    def __init__(self, dispatch_config, role="send"):
        super(RQCoupling, self).__init__(dispatch_config, role)

        if self.manage_imports():

            self.q = Queue(connection=Redis())
        else:

            logging.error("No rq Library found")

    def manage_imports(self):
        if module_exists("redis"):
            if module_exists("rq"):
                return True
        return False


    def dispatch(self, message):
        self.q.enqueue(work_container, message)

    def receive(self):
        return {}, self.q.dequeue()


class AMQPCoupling(Coupling):
    def __init__(self, dispatch_config, uri, role="send", on_receive=None):
        super(AMQPCoupling, self).__init__(dispatch_config, role)

        if self.manage_imports():
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self.hostname, port=self.port))
            self.channel = self.connection.channel()

            self.channel.queue_declare(queue=self.queue, durable=True)

            self.on_receive = on_receive

    def manage_imports(self):
        if module_exists("pika"):
            return True
        return False

    def dispatch(self, message):

        logging.info("Dispatching")
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=self.routing_key,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   ))

    def callback(self, ch, method, properties, body):

        logging.info("Received")
        ch.basic_ack(delivery_tag=method.delivery_tag)

        self.on_receive(body)


    def receive(self):

        logging.info("Receiving")

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback,
                                   queue=self.queue)

        self.channel.start_consuming()


    def close(self):

        logging.info("Receiving")

        self.connection.close()


class ZeroMQCoupling(Coupling):
    def __init__(self, dispatch_config, uri, role="send"):
        super(ZeroMQCoupling, self).__init__(dispatch_config, uri, role)

        if self.manage_imports():

            if self.io_loop and self.io_loop == "tornado":
                zmq.eventloop.ioloop.install()

            self.loop = ioloop.IOLoop.instance()

            context = zmq.Context()
            self.zmq_socket = None
            if self.role == "send":
                self.zmq_socket = context.socket(zmq.REQ)

                self.zmq_socket.connect("tcp://" + self.hostname + ":" + str(self.port))

            if self.role == "receive":
                self.zmq_socket = context.socket(zmq.REP)

                self.zmq_socket.connect("tcp://" + self.hostname + ":" + str(self.port))

                self.stream = ZMQStream(self.zmq_socket, self.loop)
                self.stream.on_recv(self.receive)

                self.loop.start()




        else:
            logging.error("No ZMQ Library found")


    def receive(self, message=None):

        if message:

            logging.info("Receiving")

            return {"uri": self.uri}, Message(message)


        else:
            message = self.zmq_socket.recv_multipart()

            return {"uri": self.uri}, Message(message)


    def dispatch(self, message):
        logging.info("Dispatching")

        self.zmq_socket.send_multipart(message)


    def manage_imports(self):
        if module_exists("zmq"):
            return True
        else:
            return False


class KafkaCoupling(Coupling):
    def __init__(self, config, uri, role="send"):
        super(KafkaCoupling, self).__init__(config, uri, role)

        if self.manage_imports():
            self.kafka = kafka.KafkaClient(self.hostname + ":" + str(self.port))


    def manage_imports(self):
        if module_exists("kafka"):
            return True
        return False

    def get_producer(self):
        self.producer = kafka.SimpleProducer(self.kafka, batch_send=True,
                                             batch_send_every_n=20,
                                             batch_send_every_t=60)

    def get_consumer(self):
        self.consumer = kafka.SimpleConsumer(self.kafka, self.group, self.topic)

    def dispatch(self, env, message):
        self.get_producer()

        logging.info("Dispatching")

        self.producer.send_messages(self.topic, message)


    def receive(self):
        self.get_consumer()

        logging.info("Receiving")

        for message in self.consumer:
            # message is raw byte string -- decode if necessary!
            # e.g., for unicode: `message.decode('utf-8')`
            yield message


    def close(self):

        logging.info("Closing")

        self.kafka.close()


class MQICoupling(Coupling):
    def dispatch(self, message):
        pass


class GearmanCoupling(Coupling):
    def dispatch(self, message):
        pass




class SMTPCoupling(Coupling):
    def __init__(self, config, role):
        super(SMTPCoupling, self).__init__(config, role)

        if self.manage_imports():
            self.build_coupling(config)

        else:
            logging.error("No  Library found")

    def build_coupling(self, config):

        self.smtp = envelopes.conn.SMTP(host=self.hostname, port=self.port, login=self.username, password=self.password,
                                        tls=config.is_ssl, timeout=config.timeout)



        # Message Folder
        # Message Regex - From, to,

        # On Complete Behaviour


    def manage_imports(self):
        if module_exists("envelopes"):
            return True
        return False

    def dispatch(self, message):
        logging.info("Dispatching")

        return self.smtp.send(message.original_message_contents)


    def complete(self, message):
        logging.info("Completed")

        return True



class BaseCouplingFactory(object):
    def get_default_config(self):
        return {}

    def process_config(self, base_config, inbound_config):
        base_config.update(inbound_config)

        return base_config

    def get_coupling_class(self):
        return None

    def build_coupling(self, config, uri):
        config = self.process_config(self.get_default_config(), config)

        coupling = self.get_coupling_class()(config, uri)
        return coupling


class CouplingFactory(object):
    def get_config_by_role(self, config, role):
        if hasattr(config, role):
            return ConfigStruct(**config.role)
        elif role in config:
            return ConfigStruct(**config[role])
        else:
            return config


    def build(self, config, uri, role):
        config = self.get_config_by_role(config, role)
        logging.info("Building Dispatcher %s" % config.dispatch_type)
        if config.dispatch_type == "rq":
            return RQCoupling(config, uri, role)
        elif config.dispatch_type == "amqp":
            return AMQPCoupling(config, uri, role)
        elif config.dispatch_type == "gearman":
            return GearmanCoupling(config, uri, role)
        elif config.dispatch_type == "beanstalk":
            return BeanStalkCoupling(config, uri, role)
        elif config.dispatch_type == "kafka":
            return KafkaCoupling(config, uri, role)
        elif config.dispatch_type == "mqi":
            return MQICoupling(config, uri, role)
        elif config.dispatch_type == "zmq":
            return ZeroMQCoupling(config, uri, role)
        elif config.dispatch_type == "smtp":
            return SMTPCoupling(config, uri, role)

        else:
            raise Exception("No Matching Coupling Found")