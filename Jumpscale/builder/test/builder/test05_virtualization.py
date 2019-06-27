from Jumpscale import j
from Jumpscale.builder.test.builder.base_test import BaseTest
import unittest
import time
from loguru import logger


class Virtualization_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("virtualization_builders_tests_{time}.log")
        logger.debug(
            "Starting of  virtualization builder testcases  which test main methods:build,install,start and stop."
        )

    def test001_docker(self):
        """ BLD-013
        *Test docker builer sandbox*
        """
        logger.debug("docker builder: run build method.")
        j.builders.virtualization.docker.build(reset=True)
        logger.debug("docker builder: run install method.")
        j.builders.virtualization.docker.install()
        logger.debug("docker builder: run start method.")
        j.builders.virtualization.docker.start()
        logger.debug("check that docker server started successfully.")
        self.assertTrue(j.sal.process.getProcessPid("containerd"))
        logger.debug("docker builder: run stop method.")
        j.builders.virtualization.docker.stop()
        logger.debug("check that docker server stopped successfully.")
        self.assertFalse(j.sal.process.getProcessPid("containerd"))
