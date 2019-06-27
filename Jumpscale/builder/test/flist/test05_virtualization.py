from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Virtualization_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("virtualization_sandbox_tests_{time}.log")
        logger.debug("Starting of virtualization sandbox testcases.")

    def test001_docker(self):
        """ SAN-014
        *Test docker builer sandbox*
        """
        logger.debug("Run docker sandbox, should succeed and upload flist on hub.")
        j.builders.virtualization.docker.sandbox(**self.sandbox_args)

        logger.debug("Deploy container with uploaded docker builder flist.")
        self.deploy_flist_container("docker")

        logger.debug("Check that docker flist works.")
        data = self.cont_client.system("/bin/sandbx/dockerd -h").get()
        self.assertIn("Usage: /sandbox/bin/dockerd", data.stdout)
