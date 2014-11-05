__author__ = 'beast'

import logging

from faucet.coupling.couplings import Coupling, SEND_ROLE, RECEIVE_ROLE, BaseCouplingFactory
from faucet.message import Message
from faucet.utils import module_exists


if module_exists("pika"):
    import pika


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