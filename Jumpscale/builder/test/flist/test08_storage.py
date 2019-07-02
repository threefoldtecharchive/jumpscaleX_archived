from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Storage_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("Storage_sandbox_tests_{time}.log")
        logger.debug("Starting of storage sandbox testcases.")

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/657")
    def test001_minio(self):
        """ SAN-017
        *Test minio builer sandbox*
        """
        logger.debug("Run  minio sandbox, should succeed and upload flist on hub.")
        j.builders.storage.minio.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded minio builder flist.")
        self.deploy_flist_container("minio")

        logger.debug("Check that minio flist works by run zdb binary, should succeed. ")
        self.assertIn("Usage: minio", self.check_container_flist("/sandbox/bin/minio"))

    def test002_restic(self):
        """ SAN-024
        *Test restic builer sandbox*
        """
        logger.debug("Run restic sandbox, should succeed and upload flist on hub.")
        j.builders.storage.restic.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded restic builder flist.")
        self.deploy_flist_container("restic")
        logger.debug("Check that restic flist works by run zdb binary, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/restic help"))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/670")
    def test003_syncthing(self):
        """ SAN-025
        *Test syncthing builer sandbox*
        """
        logger.debug("Run syncthing sandbox, should succeed and upload flist on hub.")
        j.builders.storage.syncthing.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded syncthing builder flist.")
        self.deploy_flist_container("syncthing")
        logger.debug("Check that syncthing flist works by run zdb binary, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/syncthing help"))      

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/672")
    def test004_s3scality(self):
        """ SAN-026
        *Test s3scality builer sandbox*
        """
        logger.debug("Run s3scality sandbox, should succeed and upload flist on hub.")
        j.builders.storage.s3scality.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded s3scality builder flist.")
        self.deploy_flist_container("s3scality")
        logger.debug("Check that s3scality flist works by run zdb binary, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/s3scality help"))      