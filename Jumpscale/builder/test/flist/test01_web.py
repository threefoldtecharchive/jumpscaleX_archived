from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Web_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("web_sandbox_tests_{time}.log")
        logger.debug("Starting of web sandbox testcases.")

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/654")
    def test001_caddy(self):
        """ SAN-001
        *Test caddy builer sandbox*
        """
        logger.debug("run caddy sandbox.")
        j.builders.web.caddy.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded caddy builder flist.")
        self.deploy_flist_container("caddy")
        logger.debug("Check that caddy flist works.")
        data = self.cont_client.system("/sandbox/bin/caddy -h")
        self.assertIn("Usage of sandbox/bin/caddy", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/656")
    def test002_traefik(self):
        """ SAN-002
        *Test traefik builer sandbox*
        """
        logger.debug("run traefik sandbox.")
        j.builders.web.traefik.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded traefik builder flist.")
        self.deploy_flist_container("traefik")

        logger.debug("Check that traefik flist works.")
        data = self.cont_client.system("/sandbox/bin/traefik -h")
        self.assertIn("--rancher.trace", data.get())

    def test003_nginx(self):
        """ SAN-003
        *Test nginx builer sandbox*
        """
        logger.debug("run nginx sandbox.")
        j.builders.web.nginx.sandbox(**self.sandbox_args)

        logger.debug("Deploy container with uploaded nginx builder flist.")
        self.deploy_flist_container("nginx")

        logger.debug("Check that nginx flist works.")
        data = self.cont_client.system("/sandbox/bin/nginx -h").get()
        self.assertIn("Usage: nginx", data.stderr)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/661")
    def test004_openresty(self):
        """ SAN-004
        *Test openresty builer sandbox*
        """
        logger.debug("run openresty sandbox.")
        j.builders.web.openresty.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded openresty builder flist.")
        self.deploy_flist_container("openresty")
        logger.debug("Check that openresty flist works.")
        data = self.cont_client.system("/sandbox/bin/resty -h").get()
        self.assertIn("Usage: /sandbox/bin/resty", data.stdout)
