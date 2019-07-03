from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest, time
from parameterized import parameterized


class Storage_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("storage_tests_{time}.log")
        logger.debug("Starting of db builders testcases.")

    @parameterized.expand([("minio", "minio"), ("syncthing", "syncthing"), ("s3scality", "s3scality")])
    def test001_storage_builders(self, builder, process):
        """ BLD-001
        *Test db builers sandbox*
        """
        skipped_builders = {
            "minio": "https://github.com/threefoldtech/jumpscaleX/issues/657",
            "s3scality": "https://github.com/threefoldtech/jumpscaleX/issues/671",
        }
        if builder in skipped_builders:
            self.skipTest(skipped_builders[builder])
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.storage, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.storage, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.storage, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("%s builder: run stop method." % builder)
        getattr(j.builders.storage, builder).stop()
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))

    def test002_restic(self):
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
