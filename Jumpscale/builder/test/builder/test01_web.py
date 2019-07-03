from Jumpscale import j

from .base_test import BaseTest
import unittest
import time
from loguru import logger
from parameterized import parameterized


class Web_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("web_builder_tests_{time}.log")
        logger.debug("Starting of  web builder testcases  which test main methods:build,install,start and stop.")

    @parameterized.expand([("caddy", "caddy"), ("traefik", "traefik"), ("nginx", "nginx"), ("openresty", "resty")])
    def test_web_builders(self, builder, process):
        """ BLD-001
        *Test web builers sandbox*
        """
        skipped_builders = {
            "caddy": "https://github.com/threefoldtech/jumpscaleX/issues/654",
            "traefik": "https://github.com/threefoldtech/jumpscaleX/issues/676",
            "openresty": "https://github.com/threefoldtech/jumpscaleX/issues/661",
        }
        if builder in skipped_builders:
            self.skipTest(skipped_builders[builder])
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.web, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.web, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.web, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("%s builder: run stop method." % builder)
        getattr(j.builders.web, builder).stop()
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))
