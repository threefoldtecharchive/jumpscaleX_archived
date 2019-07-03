from Jumpscale import j
from .base_test import BaseTest
import unittest
import time
from loguru import logger
from parameterized import parameterized


class Apps_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("Apps_builders_tests_{time}.log")
        logger.debug("Starting of  apps builder testcases  which test main methods:build,install,start and stop.")

    @parameterized.expand([("digitalme", "openresty"), ("freeflow", "apache2"), ("hub", "hub")])
    def test_apps_builders(self, builder, process):
        """ BLD-001
        *Test web builers sandbox*
        """
        skipped_builders = {
            "digitalme": "https://github.com/threefoldtech/jumpscaleX/issues/675",
            "hub": "https://github.com/threefoldtech/jumpscaleX/issues/676",
        }
        if builder in skipped_builders:
            self.skipTest(skipped_builders[builder])
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.apps, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.apps, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.apps, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))
