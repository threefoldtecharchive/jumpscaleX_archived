from Jumpscale import j
from Jumpscale.builder.test.builder.base_test import BaseTest
import unittest
import time
from loguru import logger


class Runtimes_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("runtimes_builders_tests_{time}.log")
        logger.debug("Starting of  runtimes builder testcases  which test main methods:build,install,start and stop.")

    def test001_golang(self):
        """ BLD-007
        *Test golang builer sandbox*
        """
        j.builders.runtimes.golang.build(reset=True)
        j.builders.runtimes.golang.install()
        self.assertTrue(j.builders.runtimes.golang.is_installed)

    def test002_lua(self):
        """ BLD-008
        *Test lua builer sandbox*
        """
        j.builders.runtimes.lua.build(reset=True)
        j.builders.runtimes.lua.install()
        j.builders.web.openresty.start()
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid("openresty")))
        j.builders.web.openresty.stop()
        time.sleep(10)
        self.assertEqual(0, len(j.sal.process.getProcessPid("openresty")))

    def test003_nimlang(self):
        """ BLD-009
        *Test nimlang builer sandbox*
        """
        j.builders.runtimes.nimlang.build(reset=True)
        j.builders.runtimes.nimlang.install()
        try:
            j.sal.process.execute("which nim")
        except:
            self.assertTrue(False)

    def test004_python(self):
        """ BLD-010
        *Test python builer sandbox*
        """
        j.builders.runtimes.python.build(reset=True)
        j.builders.runtimes.python.install()
        try:
            j.sal.process.execute("which python")
        except:
            self.assertTrue(False)

    def test005_rust(self):
        """ BLD-011
        *Test rust builer sandbox*
        """
        j.builders.runtimes.rust.build(reset=True)
        j.builders.runtimes.rust.install()
        try:
            j.sal.process.execute("which rustup")
        except:
            self.assertTrue(False)

    def test006_php(self):
        """ BLD-012
        *Test php builer sandbox*
        """
        j.builders.runtimes.php.build(reset=True)
        j.builders.runtimes.php.install()
        j.builders.runtimes.php.start()
        self.assertTrue(j.sal.process.getProcessPid("php-fpm"))
        j.builders.runtimes.php.stop()
        self.assertFalse(j.sal.process.getProcessPid("php-fpm"))
