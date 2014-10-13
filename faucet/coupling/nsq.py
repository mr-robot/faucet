__author__ = 'beast'

import logging

from faucet.coupling.couplings import Coupling, BaseCouplingFactory
from faucet.utils import module_exists


if module_exists("nsq"):
    import nsq


class NSQCoupling(Coupling):
    def __init__(self, config, uri, role="send"):
        super(NSQCoupling, self).__init__(config, uri, role)

        self.topic = config.topic
        self.channel = config.channel


    def get_reader(self, on_receive):
        if self.manage_imports():
            self.reader = nsq.Reader(message_handler=on_receive,
                                     lookupd_http_addresses=[self.hostname + ":" + str(self.port)],
                                     topic=self.topic, channel=self.channel, lookupd_poll_interval=15)

    def get_writer(self):

        self.writer = nsq.Writer([self.hostname + ":" + str(self.port)])


    def manage_imports(self):
        if module_exists("nsq"):
            return True
        return False

    def dispatch(self, env, message):
        self.get_writer()

        logging.info("Dispatching")

        self.writer.pub(self.topic, message)


    def receive(self, on_receive):
        reader = self.get_reader(on_receive)

        logging.info("Receiving")

        nsq.run()


    def close(self):

        logging.info("Closing")


class NSQFactory(BaseCouplingFactory):
    def get_default_config(self):
        return {"hostname":"127.0.0.1",
                "port":14770,
                "topic":"default",
                "channel":"default",
                "lookupd_poll_interval":15
        }

    def get_coupling_class(self):
        return NSQCoupling
