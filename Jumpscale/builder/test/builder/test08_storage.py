from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest, time


class Storage_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("storage_tests_{time}.log")
        logger.debug("Starting of db builders testcases.")

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/657")
    def test001_minio(self):
        """ BLD-024
        *Test minio builer sandbox*
        """
        logger.debug("minio builder: run build method.")
        j.builders.storage.minio.build(reset=True)
        logger.debug("minio builder: run install method.")
        j.builders.storage.minio.install()
        logger.debug("minio builder: run start method.")
        j.builders.storage.minio.start()
        logger.debug("check that minio server started successfully.")
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("minio")))
        logger.debug("minio builder: run stop method.")
        j.builders.storage.minio.stop()
        logger.debug("check that minio server stopped successfully.")
        self.assertEqual(0, len(j.sal.process.getProcessPid("minio")))

    def test002_syncthing(self):
        """ BLD-025
        *Test syncthing builer sandbox*
        """
        logger.debug("syncthing builder: run build method.")
        j.builders.storage.syncthing.build(reset=True)
        logger.debug("syncthing builder: run install method.")
        j.builders.storage.syncthing.install()
        logger.debug("syncthing builder: run start method.")
        j.builders.storage.syncthing.start()
        logger.debug("check that syncthing server started successfully.")
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid("syncthing")))
        logger.debug("syncthing builder: run stop method.")
        j.builders.storage.syncthing.stop()
        time.sleep(10)
        logger.debug("check that syncthing server stopped successfully.")
        self.assertEqual(0, len(j.sal.process.getProcessPid("syncthing")))
