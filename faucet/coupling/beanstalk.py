import logging
from faucet.coupling.couplings import Coupling, SEND_ROLE, RECEIVE_ROLE, BaseCouplingFactory
from faucet.message import Message
from faucet.utils import module_exists

__author__ = 'beast'

if module_exists("beanstalkc"):
    logging.info("Importing Beanstalk Lib")
    import beanstalkc


class BeanStalkCoupling(Coupling):
    def __init__(self, config, uri, role):
        super(BeanStalkCoupling, self).__init__(config, uri, role)

        if self.manage_imports():


            self.beanstalk = beanstalkc.Connection(host=self.hostname, port=self.port, connect_timeout=self.timeout)

            if hasattr(self, "queue"):
                if role == SEND_ROLE:
                    self.beanstalk.use(self.queue)
                elif role == RECEIVE_ROLE:
                    self.beanstalk.watch(self.queue)

        else:
            logging.error("No Beanstalk Library found")

    def get_message(self, job):

        message = Message(job.body)

        return message


    def manage_imports(self):
        if module_exists("beanstalkc"):
            return True
        return False

    def dispatch(self, env, message):
        logging.info("Dispatching")
        if "queue" in env:
            self.beanstalk.use(env["queue"])
        env["job_id"] = self.beanstalk.put(message)

        return env, None

    def receive(self, env={}):

        logging.info("Receiving")
        job = self.beanstalk.reserve()

        if job:

            message = self.get_message(job)

            return {"uri": self.uri, "job_id": job.jid}, message
        else:
            return {"uri": self.uri}, None

    def complete(self, env, message):
        logging.info("Deleting")
        self.beanstalk.delete(env["job_id"])


class BeanStalkFactory(BaseCouplingFactory):
    def get_default_config(self):
        return {}

    def get_coupling_class(self):
        return BeanStalkCoupling




