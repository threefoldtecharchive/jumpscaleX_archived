from Jumpscale import j
from .base_test import BaseTest
import unittest
import time
from loguru import logger
from parameterized import parameterized


class Runtimes_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("runtimes_builders_tests_{time}.log")
        logger.debug("Starting of  runtimes builder testcases  which test main methods:build,install,start and stop.")

    @parameterized.expand([("lua", "openresty"), ("php", "php-fpm")])
    def test_runtimes_builders(self, builder, process):
        """ BLD-001
        *Test runtimes builers sandbox*
        """
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.runtimes, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.runtimes, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.runtimes, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("%s builder: run stop method." % builder)
        getattr(j.builders.runtimes, builder).stop()
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))

    def test002_golang(self):
        """ BLD-007
        *Test golang builer sandbox*
        """
        logger.add("golang builder: run build method.")
        j.builders.runtimes.golang.build(reset=True)
        logger.add("golang builder: run install method.")
        j.builders.runtimes.golang.install()
        logger.add("Check that golang builder installed successfully")
        self.assertTrue(j.builders.runtimes.golang.is_installed)

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
        logger.add("rust builder: run build method.")
        j.builders.runtimes.rust.build(reset=True)
        logger.add("rust builder: run install method.")
        j.builders.runtimes.rust.install()
        logger.add("rust that nodejs installed successfully.")
        try:
            j.sal.process.execute("which rustup")
        except:
            self.assertTrue(False)

    def test007_nodejs(self):
        """ BLD-000
        *Test nodejs builer sandbox*
        """
        logger.add("nodejs builder: run build method.")
        j.builders.runtimes.nodejs.build(reset=True)
        logger.add("nodejs builder: run install method.")
        j.builders.runtimes.nodejs.install()
        logger.add("check that nodejs installed successfully.")
        self.assertTrue(j.sal.process.execute("which nodejs"))
