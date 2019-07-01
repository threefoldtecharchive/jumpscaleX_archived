from Jumpscale import j
from .base_test import BaseTest
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
        logger.debug("coredns builder: run build method.")
        j.builders.network.coredns.build(reset=True)
        logger.debug("coredns builder: run install method.")
        j.builders.network.coredns.install()
        logger.debug("coredns builder: run start method.")
        j.builders.network.coredns.start()
        logger.debug("check that coredns builder is started successfully ")
        self.assertTrue(j.sal.process.getProcessPid("coredns"))
        logger.debug("coredns builder: run stop method.")
        j.builders.network.coredns.stop()
        time.sleep(10)
        self.assertFalse(j.sal.process.getProcessPid("coredns"))

    def test002_zerotier(self):
        """ BLD-006
        *Test zerotier builer sandbox*
        """
        logger.debug("zerotier builder: run build method.")
        j.builders.network.zerotier.build(reset=True)
        logger.debug("zerotier builder: run install method.")
        j.builders.network.zerotier.install()
        logger.debug("zerotier builder: run start method.")
        j.builders.network.zerotier.start()
        logger.debug("check that zerotier builder is started successfully ")
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("zerotier-one")))
        logger.debug("zerotier builder: run stop method.")
        j.builders.network.zerotier.stop()
        logger.debug("check that zerotier builder is stopped successfully ")
        self.assertEqual(0, len(j.sal.process.getProcessPid("zerotier-one")))
