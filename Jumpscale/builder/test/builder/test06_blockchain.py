from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest
from parameterized import parameterized


class Blockchain_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("blockchain_tests_{time}.log")
        logger.debug("Starting of blockchain testcases.")

    @parameterized.expand([("bitcoin", "bitcoind"), ("ethereum", "ethereum")])
    def test_blockchain_builders(self, builder, process):
        """ BLD-001
        *Test web builers sandbox*
        """
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.blockchain, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.blockchain, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.blockchain, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("%s builder: run stop method." % builder)
        getattr(j.builders.blockchain, builder).stop()
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))
