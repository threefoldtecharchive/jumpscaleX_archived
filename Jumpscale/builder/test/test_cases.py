from Jumpscale import j
from Jumpscale.builder.test.base_test import BaseTest
import unittest 

class TestCases(BaseTest):
    def test001_caddy(self):
        j.builder.web.caddy.sandbox(zhub_instance=self.hub_instance, reset=True)
        j.builder.web.caddy.create_flist(self.hub_instance)
        self.deploy_flist_container('caddy')
        data = self.cont_client.system("/sandbox/bin/caddy -h")
        self.assertIn("Usage of sandbox/bin/caddy", data.stdout)

    def test002_traefik(self):
        j.builder.web.traefik.sandbox(zhub_instance=self.hub_instance, reset=True)
        j.builder.web.caddy.create_flist(self.hub_instance)
        self.deploy_flist_container('traefik')
        data = self.cont_client.system("/sandbox/bin/traefik -h")
        self.assertIn("--rancher.trace", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/189")
    def test003_nginx(self):
        j.builder.web.nginx.sandbox(zhub_instance=self.hub_instance, reset=True)
        j.builder.web.nginx.create_flist(self.hub_instance)
        self.deploy_flist_container('nginx')
        data = self.cont_client.system("/sanaxdbox/bin/ngnix -h")
        self.assertIn("Usage: nginx", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/205")
    def test004_lua(self):
        j.builder.web.nginx.sandbox(zhub_instance=self.hub_instance, reset=True)
        j.builder.web.nginx.create_flist(self.hub_instance)
        self.deploy_flist_container('nginx')
        data = self.cont_client.system("/sandbox/bin/ngnix -h")
        self.assertIn("Usage: nginx", data.stdout)

    @unitteast.skip("https://github.com/threefoldtech/jumpscaleX/issues/186")
    def test005_openresty(self):
        j.builder.web.openresty.sandbox(zhub_instance=self.hub_instance, reset=True)
        j.builder.web.openresty.create_flist(self.hub_instance)
        self.deploy_flist_container('openresty')
        data = self.cont_client.system("/sandbox/bin/resty -h")
        self.assertIn("Usage: /sandbox/bin/resty", data.stdout)

    def test006_etcd(self):
        j.builder.db.etcd.sandbox(zhub_instance=self.hub_instance, reset=True)
        j.builder.db.etcd.create_flist(self.hub_instance)
        self.deploy_flist_container('etcd')
        data = self.cont_client.system("/sandbox/bin/etcd -h")
        self.assertIn("--snapshot-count", data.stdout)

    
