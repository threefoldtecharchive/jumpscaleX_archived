from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest, time


class Libs_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("Libs_tests_{time}.log")
        logger.debug("Starting of Libs builders testcases.")

    def test001_capnp(self):
        """ BLD-026
        *Test capnp builer sandbox*
        """
        j.builders.libs.capnp.build(reset=True)
        j.builders.libs.capnp.install()
        j.builders.libs.capnp.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("capnp")))
        j.builders.libs.capnp.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("capnp")))

    def test002_cmake(self):
        """ BLD-027
        *Test cmake builer sandbox*
        """
        logger.debug("cmake builder: run build method.")
        j.builders.libs.cmake.build(reset=True)
        logger.debug("cmake builder: run install method.")
        j.builders.libs.cmake.install()
        try:
            logger.debug("check that cmake is installed successfully")
            j.sal.process.execute("which cmake")
        except:
            self.assertTrue(False)

    def test003_libffi(self):
        """ BLD-028
        *Test libffi builer sandbox*
        """
        j.builders.libs.libffi.build(reset=True)
        j.builders.libs.libffi.install()
        try:
            j.sal.process.execute("which libtoolize")
        except:
            self.assertTrue(False)

    def test004_brotli(self):
        """ BLD-029
        *Test brotli builer sandbox*
        """
        j.builders.libs.brotli.build(reset=True)
        j.builders.libs.brotli.install()
        try:
            j.sal.process.execute("which brotli")
        except:
            self.assertTrue(False)
