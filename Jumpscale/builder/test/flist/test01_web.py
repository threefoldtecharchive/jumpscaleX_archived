from parameterized import parameterized
from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest

class Web_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("web_sandbox_tests_{time}.log")
        logger.debug("Starting of web sandbox testcases.")

    @parameterized.expand([("caddy", "caddy"), ("traefik", "traefik"), ("nginx", "nginx"), ("openresty", "openresty")])
    def test_web_flists(self, flist, binary):
        """ SAN-001
        *Test web builers sandbox*
        """
        skipped_flists = {
            "caddy": "https://github.com/threefoldtech/jumpscaleX/issues/654",
            "traefik": "https://github.com/threefoldtech/jumpscaleX/issues/656",
            "openresty": "https://github.com/threefoldtech/jumpscaleX/issues/661",
        }

        if flist in skipped_flists:
            self.skipTest(skipped_flists[flist])
        logger.info("run %s sandbox." % flist)
        getattr(j.builders.web, flist).sandbox(**self.sandbox_args)
        logger.info("Deploy container with uploaded %s flist." % flist)
        self.deploy_flist_container("%s" % flist)
        logger.info("Check that %s flist works." % flist)
        self.assertIn("Usage: ", self.check_container_flist("/sandbox/bin/%s -h") % flist)

