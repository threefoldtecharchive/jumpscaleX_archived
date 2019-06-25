from Jumpscale import j
from base_test import BaseTest
from loguru import logger
import unittest


class TestCases(BaseTest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.add("sandbox_tests.log")
        logger.debug("Starting of sandbox testcases.")

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
        logger.debug("Run docker sandbox, should succeed and upload flist on hub.")
        j.builders.virtualization.docker.sandbox(
            zhub_instance=self.hub_instance,
            reset=True,
            create_flist=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        logger.debug("Deploy container with uploaded zdb builder flist.")
        self.deploy_flist_container("docker")

        logger.debug("Check that docker flist works.")
        self.assertIn("Usage:", self.check_container_flist("/bin/sandbx/dockerd -h"))

    def test009_zdb(self):
        logger.debug("run zdb sandbox, should succeed and upload flist on hub.")
        j.builders.db.zdb.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        logger.debug("deploy container with uploaded zdb builder flist.")
        self.deploy_flist_container("0-db")

        logger.debug("Check that zdb flist works by run zdb binary, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/bin/sandbox/zdb -h"))

    def test010_digitalme(self):
        j.builders.apps.digitalme.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )
        self.deploy_flist_container("digitalme")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/openresty -h"))

    def test011_postgresql(self):
        j.builders.db.postgres.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )        
        self.deploy_flist_container("postgresql")
        self.assertIn("PostgreSQL server", self.check_container_flist("/sandbox/bin/postgres -h"))

    def test012_redis(self):
        j.builders.db.redis.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )     
        self.deploy_flist_container("redis")
        self.assertIn("Usage: redis-cli", self.check_container_flist("/sandbox/bin/redis-cli -h"))