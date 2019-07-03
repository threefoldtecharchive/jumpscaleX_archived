from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Runtimes_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("runtimes_sandbox_tests_{time}.log")
        logger.debug("Starting of runtimes sandbox testcases.")

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/665")
    def test001_lua(self):
        """ SAN-005
        *Test lua builer sandbox*
        """
        logger.debug("run lua sandbox.")
        j.builders.runtimes.lua.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded lua builder flist.")
        self.deploy_flist_container("lua")
        logger.debug("Check that lua flist works.")
        data = self.cont_client.system("/sandbox/bin/lua -h").get()
        self.assertIn("Usage: lua", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/678")
    def test002_golang(self):
        """ SAN-027
        *Test golang builer sandbox*
        """        
        logger.debug("Run  golang sandbox, should succeed and upload flist on hub.")
        j.builders.runtimes.golang.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded golang builder flist.")
        self.deploy_flist_container("golang")
        logger.debug("Check that golang flist works by checking openssl file existing, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/golang help"))
