from Jumpscale import j
from base_test import BaseTest
from loguru import logger
import unittest


class Network_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("network_sandbox_tests_{time}.log")
        logger.debug("Starting of network sandbox testcases.")

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/201")
    def test001_coredns(self):
        """ SAN-013
        *Test coredns builer sandbox*
        """
        j.builders.network.coredns.sandbox(**self.sandbox_args)
        self.deploy_flist_container("coredns")
        data = self.cont_client.system("/sandbox/bin/coredns -h").get()
        self.assertIn("Usage: ", data.stdout)
