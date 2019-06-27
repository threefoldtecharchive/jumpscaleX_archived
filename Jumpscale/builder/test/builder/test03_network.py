from Jumpscale import j
from Jumpscale.builder.test.builder.base_test import BaseTest
import unittest
import time
from loguru import logger


class Network_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("network_builders_tests_{time}.log")
        logger.debug("Starting of  network builder testcases  which test main methods:build,install,start and stop.")

    def test001_coredns(self):
        """ BLD-006
        *Test coredns builer sandbox*
        """
        j.builders.network.coredns.build(reset=True)
        j.builders.network.coredns.install()
        j.builders.network.coredns.start()
        self.assertTrue(j.sal.process.getProcessPid("coredns"))
        j.builders.network.coredns.stop()
        time.sleep(10)
        self.assertFalse(j.sal.process.getProcessPid("coredns"))

    def test002_zerotier(self):
        """ BLD-006
        *Test zerotier builer sandbox*
        """
        j.builders.network.zerotier.build(reset=True)
        j.builders.network.zerotier.install()
        j.builders.network.zerotier.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("zerotier")))
        j.builders.network.zerotier.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("zerotier")))
