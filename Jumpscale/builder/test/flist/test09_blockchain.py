from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Blockchain_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("blockchain_sandbox_tests_{time}.log")
        logger.debug("Starting of blockchain sandbox testcases.")
    
    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/677")
    def test001_ripple(self):
        """ SAN-0027
        *Test ripple builer sandbox*
        """
        logger.debug("run ripple sandbox.")
        j.builders.blockchain.ripple.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded ripple builder flist.")
        self.deploy_flist_container("ripple")
        logger.debug("Check that ripple flist works.")
        self.assertIn("Usage: ", self.check_container_flist("/sandbox/bin/ripple help"))     
