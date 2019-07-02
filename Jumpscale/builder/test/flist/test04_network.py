from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Network_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("network_sandbox_tests_{time}.log")
        logger.debug("Starting of network sandbox testcases.")

    def test001_coredns(self):
        """ SAN-013
        *Test coredns builer sandbox*
        """
        logger.debug("run coredns sandbox.")
        j.builders.network.coredns.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded coredns builder flist.")
        self.deploy_flist_container("coredns")
        logger.debug("Check that coredns flist works.")
        data = self.cont_client.system("/sandbox/bin/coredns -h").get()
        self.assertIn("Usage: ", data.stdout)

    def test002_zerotier(self):
        """ SAN-019
        *Test zerotier builer sandbox*
        """
        logger.debug("run zerotier sandbox.")
        j.builders.network.zerotier.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded zerotier builder flist.")
        self.deploy_flist_container("zerotier")
        logger.debug("Check that zerotier flist works.")
        data = self.cont_client.system("/sandbox/bin/zerotier-one -h").get()
        self.assertIn("Usage: ", data.stdout)
