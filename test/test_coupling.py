from faucet import main

__author__ = 'beast'
import unittest
from faucet.coupling.couplings import *

from random import randint

import beanstalkc

class TestCouplings(unittest.TestCase):

    def setUp(self):
        pass



    def test_beanstalkd_coupling(self):

        config = ConfigStruct(**{"dsn" : "beanstalk://127.0.0.1:11300", "timeout":10, "queue":"test-queue"})
        role="send"
        uri="test"

        bs = BeanStalkCoupling(config=config, role=role, uri=uri)

        role = "receive"

        bs_2 = BeanStalkCoupling(config=config, role=role, uri=uri)

        test_message = "test" + str(randint(0,1000))
        env, message = bs.dispatch({},test_message)

        self.assertTrue("job_id" in env)
        self.assertTrue(env["job_id"] is not None)

        job_id = env["job_id"]



        env, message = bs_2.receive()

        bs_2.complete(env,None)

        self.assertTrue("job_id" in env)
        self.assertTrue(env["job_id"] is not None)

        self.assertTrue("job_id" in env)

        self.assertEquals(test_message, message.original_message_contents)

        self.assertTrue(env["job_id"] == job_id)

    def test_kafka_coupling(self):

        config = ConfigStruct(**{"dsn" : "kafka://127.0.0.1:9092", "timeout":10, "topic":"test-queue"})
        role="send"
        uri="test"

        kf = KafkaCoupling(config=config, role=role, uri=uri)

        role = "receive"

        kf_2 = KafkaCoupling(config=config, role=role, uri=uri)

        test_message = "test" + str(randint(0,1000))
        env, message = kf.dispatch({},test_message)

        job_id = env["job_id"]



        env, message = kf_2.receive()

        self.assertEquals(test_message, message)

    def test_kafka_coupling(self):

        config = ConfigStruct(**{"dsn" : "kafka://127.0.0.1:9092", "timeout":10, "topic":"test-queue"})
        role="send"
        uri="test"

        kf = KafkaCoupling(config=config, role=role, uri=uri)

        role = "receive"

        kf_2 = KafkaCoupling(config=config, role=role, uri=uri)

        test_message = "test" + str(randint(0,1000))
        env, message = kf.dispatch({},test_message)

        job_id = env["job_id"]



        env, message = kf_2.receive()

        self.assertEquals(test_message, message)


    def test_nsq_coupling(self):

        config = ConfigStruct(**{"dsn" : "nsq://127.0.0.1:9092", "timeout":10, "topic":"test-queue"})
        role="send"
        uri="test"

        nf = NSQCoupling(config=config, role=role, uri=uri)

        role = "receive"

        nf_2 = NSQCoupling(config=config, role=role, uri=uri)

        test_message = "test" + str(randint(0,1000))
        env, message = nf.dispatch({},test_message)

        job_id = env["job_id"]



        env, message = nf_2.receive()

        self.assertEquals(test_message, message)




if __name__ == '__main__':
    unittest.main()