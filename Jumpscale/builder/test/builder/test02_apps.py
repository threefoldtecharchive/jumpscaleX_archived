from Jumpscale import j
from .base_test import BaseTest
import unittest
import time
from loguru import logger


class Apps_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("Apps_builders_tests_{time}.log")
        logger.debug("Starting of  apps builder testcases  which test main methods:build,install,start and stop.")

    def test001_digitalme(self):
        """ BLD-004
        *Test digitalme builer sandbox*
        """
        logger.debug("DigitalMe builder: run build method. ")
        j.builders.apps.digitalme.build(reset=True)
        logger.debug("DigitalMe builder: run install method. ")
        j.builders.apps.digitalme.install()
        logger.debug("DigitalMe builder: run start method. ")
        j.builders.apps.digitalme.start()
        logger.debug("check that DigitalMe builder is started successfully ")
        self.assertTrue(len(j.sal.process.getProcessPid("openresty")))
        logger.debug("DigitalMe builder: run stop method. ")
        j.builders.apps.digitalme.stop()
        logger.debug("check that DigitalMe builder is stopped successfully ")
        self.assertEqual(0, len(j.sal.process.getProcessPid("openresty")))

    def test002_freeflow(self):
        """ BLD-005
        *Test freeflow builer sandbox*
        """
        j.builders.apps.freeflow.build(reset=True)
        j.builders.apps.freeflow.install(reset=True)
        j.builders.apps.freeflow.start()
        self.assertTrue(len(j.sal.process.getProcessPid("apache2")))
        j.builders.apps.freeflow.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("apache2")))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/669")
    def test003_hub(self):
        """ BLD-000
        *Test hub builer sandbox*
        """
        logger.debug("Hub builder: run build method. ")
        j.builders.apps.hub.build(reset=True)
        logger.debug("Hub builder: run install method. ")
        j.builders.apps.hub.install(reset=True)
        logger.debug("Hub builder: run start method. ")
        j.builders.apps.hub.start()
        logger.debug("check that Hub builder is started successfully ")
        self.assertTrue(len(j.sal.process.getProcessPid("hub")))
        logger.debug("Hub builder: run stop method. ")
        j.builders.apps.hub.stop()
        logger.debug("check that Hub builder is stopped successfully ")
        self.assertEqual(0, len(j.sal.process.getProcessPid("hub")))
