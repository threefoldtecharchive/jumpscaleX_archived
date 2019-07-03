from Jumpscale import j
from .base_test import BaseTest
import unittest
import time
from loguru import logger
from parameterized import parameterized


class Virtualization_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("virtualization_builders_tests_{time}.log")
        logger.debug(
            "Starting of  virtualization builder testcases  which test main methods:build,install,start and stop."
        )

    @parameterized.expand([("docker", "containerd")])
    def test_virtualization_builders(self, builder, process):
        """ BLD-001
        *Test virtualization builers sandbox*
        """
        skipped_builders = {"docker": "https://github.com/threefoldtech/jumpscaleX/issues/664"}
        if builder in skipped_builders:
            self.skipTest(skipped_builders[builder])
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.virtualization, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.virtualization, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.virtualization, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("%s builder: run stop method." % builder)
        getattr(j.builders.virtualization, builder).stop()
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))

