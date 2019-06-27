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
