from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest, time
from parameterized import parameterized


class StorageTestCases(BaseTest):
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
        self.info(" %s builder: run build method.".format(builder))
        getattr(j.builders.storage, builder).build()
        self.info(" %s builder: run install  method.".format(builder))
        getattr(j.builders.storage, builder).install()
        self.info(" %s builder: run start method.".format(builder))
        getattr(j.builders.storage, builder).start()
        self.info(" check that %s server started successfully.".format(builder))
        self.small_sleep()
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        self.info(" %s builder: run stop method.".format(builder))
        getattr(j.builders.storage, builder).stop()
        self.info(" check that %s server stopped successfully.".format(builder))
        self.small_sleep()
        self.assertFalse(len(j.sal.process.getProcessPid(process)))

    def test002_restic(self):
        """ BLD-033
        *Test restic builer sandbox*
        """
        self.info(" restic builder: run build method.")
        j.builders.storage.restic.build(reset=True)
        self.info(" restic builder: run install method.")
        j.builders.storage.restic.install()
        try:
            self.info(" check that libffi is installed successfully")
            j.sal.process.execute("which restic")
        except:
            self.assertTrue(False)
