from Jumpscale import j
from Jumpscale.builder.test.base_test import BaseTest


class TestCases(BaseTest):
    def test001_caddy(self):
        j.builder.web.caddy.builder()
        j.builder.web.caddy.sandbox()
        j.builder.web.caddy.create_flist(self.hub_instance)
        self.deploy_flist_container('caddy')
        data = self.cont_client.system("/sandbox/bin/caddy -h")
        self.assertIn("Usage of sandbox/bin/caddy", data.stdout)

    def test002_traefik(self):
        j.builder.web.traefik.build()
        j.builder.web.traefik.sandbox()
        j.builder.web.caddy.create_flist(self.hub_instance)
        self.deploy_flist_container('traefik')
        data = self.cont_client.system("/sandbox/bin/traefik -h")
        self.assertIn("--rancher.trace", data.stdout)

