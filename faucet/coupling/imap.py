__author__ = 'beast'

from faucet.coupling.couplings import Coupling
from faucet.utils import module_exists
from faucet.message import Message
import logging


if module_exists("imbox"):
    logging.info("Importing Imbox Lib")
    import imbox

class IMAPCoupling(Coupling):
    def __init__(self, config, role):
        super(IMAPCoupling, self).__init__(config, role)

        if self.manage_imports():
            self.build_coupling(config)

        else:
            logging.error("No  Library found")

    def build_coupling(self, config):

        self.imbox = imbox.Imbox(self.hostname,
                                 username=self.username,
                                 password=self.password,
                                 ssl=config.is_ssl)

        # Message Folder
        # Message Regex - From, to,

        # On Complete Behaviour


    def manage_imports(self):
        if module_exists("imbox"):
            return True
        return False

    def dispatch(self, message):
        logging.info("Dispatching")
        return None

    def receive(self):

        logging.info("Receiving")

        for message in self.imbox.messages(unread=True):
            yield Message(message)


    def complete(self, message):
        logging.info("Deleting")

        return True