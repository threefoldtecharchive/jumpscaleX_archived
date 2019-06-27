from Jumpscale import j
from base_test import BaseTest
from loguru import logger
import unittest


class Apps_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("Libs_sandbox_tests_{time}.log")
        logger.debug("Starting of Libs sandbox testcases.")

    def test001_cmake(self):
        """ SAN-016
        *Test cmake builer sandbox*
        """
        logger.debug("run cmake sandbox, should succeed and upload flist on hub.")
        j.builders.lib.cmake.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded cmake builder flist.")
        self.deploy_flist_container("cmake")
        logger.debug("Check that cmake flist works by run cmake command, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/cmake -h"))
