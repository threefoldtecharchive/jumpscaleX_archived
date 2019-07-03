from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest, time
from parameterized import parameterized


class Libs_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("Libs_tests_{time}.log")
        logger.debug("Starting of Libs builders testcases.")

    @parameterized.expand([("capnp", "capnp"), ("syncthing", "syncthing")])
    def test_libs_builders(self, builder, process):
        """ BLD-001
        *Test libs builers sandbox*
        """
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.libs, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.libs, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.libs, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("%s builder: run stop method." % builder)
        getattr(j.builders.libs, builder).stop()
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))

    def test002_libffi(self):
        """ BLD-028
        *Test libffi builer sandbox*
        """
        logger.debug("libffi builder: run build method.")
        j.builders.libs.libffi.build(reset=True)
        logger.debug("libffi builder: run install method.")
        j.builders.libs.libffi.install()
        try:
            logger.debug("check that libffi is installed successfully")
            j.sal.process.execute("which libtoolize")
        except:
            self.assertTrue(False)

    def test003_brotli(self):
        """ BLD-029
        *Test brotli builer sandbox*
        """
        logger.debug("brotli builder: run build method.")
        j.builders.libs.brotli.build(reset=True)
        logger.debug("brotli builder: run install method.")
        j.builders.libs.brotli.install()
        try:
            logger.debug("check that brotli is installed successfully")
            j.sal.process.execute("which brotli")
        except:
            self.assertTrue(False)

    def test004_openssl(self):
        """ BLD-032
        *Test openssl builer sandbox*
        """
        logger.debug("openssl builder: run build method.")
        j.builders.libs.openssl.build(reset=True)
        logger.debug("openssl builder: run install method.")
        j.builders.libs.openssl.install()
        try:
            logger.debug("check that openssl is installed successfully")
            j.sal.process.execute("which openssl")
        except:
            self.assertTrue(False)

