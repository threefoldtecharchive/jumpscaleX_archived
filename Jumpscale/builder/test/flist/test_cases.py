from Jumpscale import j
from base_test import BaseTest
import unittest


class TestCases(BaseTest):
    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/299")
    def test001_caddy(self):
        j.builders.web.caddy.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("caddy")
        data = self.cont_client.system("/sandbox/bin/caddy -h")
        self.assertIn("Usage of sandbox/bin/caddy", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/299")
    def test002_traefik(self):
        j.builders.web.traefik.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("traefik")
        data = self.cont_client.system("/sandbox/bin/traefik -h")
        self.assertIn("--rancher.trace", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/189")
    def test003_nginx(self):
        j.builders.web.nginx.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("nginx")
        data = self.cont_client.system("/sanaxdbox/bin/ngnix -h")
        self.assertIn("Usage: nginx", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/205")
    def test004_lua(self):
        j.builders.web.nginx.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("nginx")
        data = self.cont_client.system("/sandbox/bin/ngnix -h")
        self.assertIn("Usage: nginx", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/186")
    def test005_openresty(self):
        j.builders.web.openresty.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("openresty")
        data = self.cont_client.system("/sandbox/bin/resty -h")
        self.assertIn("Usage: /sandbox/bin/resty", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/299")
    def test006_etcd(self):
        j.builders.db.etcd.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("etcd")
        data = self.cont_client.system("/sandbox/bin/etcd -h")
        self.assertIn("--snapshot-count", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/201")
    def test007_coredns(self):
        j.builders.network.coredns.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        j.builders.db.etcd.create_flist(self.hub_instance)
        self.deploy_flist_container("coredns")

    def test008_docker(self):
        j.builders.virtualization.docker.sandbox(
            zhub_client=self.zhub,
            reset=True,
            create_flist=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("docker")
        self.assertIn("Usage:", self.check_container_flist("/bin/sandbx/dockerd -h"))

    def test009_zdb(self):
        j.builders.db.zdb.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("0-db")
        self.assertIn("Usage:", self.check_container_flist("/bin/sandbox/zdb -h"))
