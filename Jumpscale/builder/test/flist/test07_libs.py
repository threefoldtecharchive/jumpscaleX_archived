from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Apps_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("Libs_sandbox_tests_{time}.log")
        logger.debug("Starting of Libs sandbox testcases.")

    def test001_cmake(self):
        """ SAN-016
        *Test cmake builer sandbox*
        """
        logger.debug("run cmake sandbox, should succeed and upload flist on hub.")
        j.builders.libs.cmake.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded cmake builder flist.")
        self.deploy_flist_container("cmake")
        logger.debug("Check that cmake flist works by run cmake command, should succeed. ")
        self.assertIn("Usage", self.check_container_flist("/sandbox/bin/cmake"))
    
    def test002_capnp(self):
        """ SAN-020
        *Test capnp builer sandbox*
        """
        logger.debug("Run  capnp sandbox, should succeed and upload flist on hub.")
        j.builders.libs.capnp.sandbox(**self.sandbox_args) 
        logger.debug("Deploy container with uploaded capnp builder flist.")
        self.deploy_flist_container("capnp")
        logger.debug("Check that capnp flist works by checking capnp file existing, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/capnp --help")) 

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/660")
    def test003_libffi(self):
        """ SAN-021
        *Test libffi builer sandbox*
        """
        logger.debug("Run  libffi sandbox, should succeed and upload flist on hub.")
        j.builders.libs.libffi.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded libffi builder flist.")
        self.deploy_flist_container("libffi")
        logger.debug("Check that libffi flist works by checking libffi file existing, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/libtoolize --help"))

    def test004_Brotli(self):
        """ SAN-022
        *Test brotli builer sandbox*
        """
        logger.debug("Run  brotli sandbox, should succeed and upload flist on hub.")
        j.builders.libs.brotli.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded brotli builder flist.")
        self.deploy_flist_container("brotli")
        logger.debug("Check that brotli flist works by checking brotli file existing, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/brotli -h"))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/662")
    def test005_openssl(self):
        """ SAN-023
        *Test openssl builer sandbox*
        """ 
        logger.debug("Run  openssl sandbox, should succeed and upload flist on hub.")
        j.builders.libs.openssl.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded openssl builder flist.")
        self.deploy_flist_container("openssl")
        logger.debug("Check that openssl flist works by checking openssl file existing, should succeed. ")
        self.assertIn("Standard commands", self.check_container_flist("/sandbox/bin/openssl help"))     



