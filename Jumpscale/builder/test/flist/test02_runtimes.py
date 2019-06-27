from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Runtimes_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("runtimes_sandbox_tests_{time}.log")
        logger.debug("Starting of runtimes sandbox testcases.")

    # @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/205")
    def test001_lua(self):
        """ SAN-005
        *Test lua builer sandbox*
        """
        j.builders.runtimes.lua.sandbox(**self.sandbox_args)
        self.deploy_flist_container("lua")
        data = self.cont_client.system("/sandbox/bin/lua -h").get()
        self.assertIn("Usage: lua", data.stdout)
