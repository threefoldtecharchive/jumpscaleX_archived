from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Apps_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("Apps_sandbox_tests_{time}.log")
        logger.debug("Starting of apps sandbox testcases.")

    def test001_digitalme(self):
        """ SAN-015
        *Test digitalme builer sandbox*
        """
        logger.debug("run digitalme sandbox, should succeed and upload flist on hub.")
        j.builders.apps.digitalme.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded digitalme builder flist.")
        self.deploy_flist_container("digitalme")
        logger.debug("Check that digitalme flist works by run openresty command, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/openresty -h"))

    def test002_freeflow(self):
        """ SAN-031
        *Test freeflow builer sandbox*
        """
        logger.debug("Run  freeflow sandbox, should succeed and upload flist on hub.")
        j.builders.apps.freeflow.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded freeflow builder flist.")
        self.deploy_flist_container("freeflow")
        logger.debug("Check that freeflow flist works by run apache2 binary, should succeed. ")
        self.assertIn("Usage: apache2", self.check_container_flist("/sandbox/bin/apache2 -h"))

