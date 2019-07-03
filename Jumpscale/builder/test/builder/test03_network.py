from Jumpscale import j
from .base_test import BaseTest
import unittest
import time
from loguru import logger
from parameterized import parameterized


class Network_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("network_builders_tests_{time}.log")
        logger.debug("Starting of  network builder testcases  which test main methods:build,install,start and stop.")

    @parameterized.expand([("coredns", "coredns"), ("zerotier", "zerotier-one")])
    def test_network_builders(self, builder, process):
        """ BLD-001
        *Test network builers sandbox*
        """
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.network, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.network, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.network, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("%s builder: run stop method." % builder)
        getattr(j.builders.network, builder).stop()
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))
