from Jumpscale import j

from .base_test import BaseTest
import unittest
import time
from loguru import logger


class Web_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("web_builder_tests_{time}.log")
        logger.debug("Starting of  web builder testcases  which test main methods:build,install,start and stop.")

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/654")
    def test001_caddy(self):
        """ BLD-001
        *Test caddy builer sandbox*
        """
        logger.debug("caddy builder: run build method.")
        j.builders.web.caddy.build(reset=True)
        logger.debug("caddy builder: run build method.")
        j.builders.web.caddy.install()
        logger.debug("caddy builder: run build method.")
        j.builders.web.caddy.start()
        logger.debug("check that caddy server started successfully.")
        self.assertEqual(1, len(j.sal.process.getProcessPid("caddy")))
        logger.debug("caddy builder: run build method.")
        j.builders.web.caddy.stop()
        logger.debug("check that caddy server stopped successfully.")
        self.assertEqual(0, len(j.sal.process.getProcessPid("caddy")))

    def test002_nginx(self):
        """ BLD-002
        *Test nginx builer sandbox*
        """
        logger.debug("nginx builder: run build method.")
        j.builders.web.nginx.build(reset=True)
        logger.debug("nginx builder: run build method.")
        j.builders.web.nginx.install()
        logger.debug("nginx builder: run build method.")
        j.builders.web.nginx.start()
        logger.debug("check that nginx server started successfully.")
        self.assertTrue(len(j.sal.process.getProcessPid("nginx")))
        logger.debug("nginx builder: run build method.")
        j.builders.web.nginx.stop()
        logger.debug("check that nginx server stopped successfully.")
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid("nginx")))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/656")
    def test003_traefik(self):
        """ BLD-003
        *Test traefik builer sandbox*
        """
        logger.debug("traefik builder: run build method.")
        j.builders.web.traefik.build(reset=True)
        logger.debug("traefik builder: run install method.")
        j.builders.web.traefik.install()
        logger.debug("traefik builder: run start method.")
        j.builders.web.traefik.start()
        logger.debug("check that traefik server started successfully.")
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("traefik")))
        logger.debug("traefik builder: run stop method.")
        j.builders.web.traefik.stop()
        logger.debug("check that traefik server stopped successfully.")
        self.assertEqual(0, len(j.sal.process.getProcessPid("traefik")))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/661")
    def test004_openresty(self):
        """ BLD-031
        *Test OpenResty builer sandbox*
        """
        logger.debug("OpenResty builder: run build method.")
        j.builders.web.openresty.build(reset=True)
        logger.debug("OpenResty builder: run install method.")
        j.builders.web.openresty.install()
        logger.debug("OpenResty builder: run start method.")
        j.builders.web.openresty.start()
        logger.debug("check that OpenResty server started successfully.")
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("resty")))
        logger.debug("openresty builder: run stop method.")
        j.builders.web.openresty.stop()
        logger.debug("check that resty server stopped successfully.")
        self.assertEqual(0, len(j.sal.process.getProcessPid("resty")))
