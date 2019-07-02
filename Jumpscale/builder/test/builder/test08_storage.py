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

    def test003_restic(self):
        """ BLD-033
        *Test restic builer sandbox*
        """
        logger.debug("restic builder: run build method.")
        j.builders.storage.restic.build(reset=True)
        logger.debug("restic builder: run install method.")
        j.builders.storage.restic.install()
        try:
            logger.debug("check that libffi is installed successfully")
            j.sal.process.execute("which restic")
        except:
            self.assertTrue(False)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/671")
    def test004_s3scality(self):
        """ BLD-034
        *Test s3scality builer sandbox*
        """
        logger.debug("s3scality builder: run build method.")
        j.builders.storage.s3scality.build(reset=True)
        logger.debug("s3scality builder: run install method.")
        j.builders.storage.s3scality.install()
        logger.debug("s3scality builder: run start method.")
        j.builders.storage.s3scality.start()
        logger.debug("check that s3scality  server started successfully.")
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid("s3scality")))
        logger.debug("s3scality builder: run stop method.")
        j.builders.storage.s3scality.stop()
        time.sleep(10)
        logger.debug("check that s3scality server stopped successfully.")
        self.assertEqual(0, len(j.sal.process.getProcessPid("s3scality")))