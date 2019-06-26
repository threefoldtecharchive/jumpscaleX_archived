from Jumpscale import j
from base_test import BaseTest
from loguru import logger
import unittest


class TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("sandbox_tests_{time}.log")
        logger.debug("Starting of sandbox testcases.")

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/654")
    def test001_caddy(self):
        logger.debug("run caddy sandbox.")
        j.builders.web.caddy.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded caddy builder flist.")
        self.deploy_flist_container("caddy")
        logger.debug("Check that caddy flist works.")
        data = self.cont_client.system("/sandbox/bin/caddy -h")
        self.assertIn("Usage of sandbox/bin/caddy", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/656")
    def test002_traefik(self):
        logger.debug("run traefik sandbox.")
        j.builders.web.traefik.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded traefik builder flist.")
        self.deploy_flist_container("traefik")

        logger.debug("Check that traefik flist works.")
        data = self.cont_client.system("/sandbox/bin/traefik -h")
        self.assertIn("--rancher.trace", data.get())

    def test003_nginx(self):
        logger.debug("run nginx sandbox.")
        j.builders.web.nginx.sandbox(**self.sandbox_args)
        logger.debug("Deploy container with uploaded nginx builder flist.")
        self.deploy_flist_container("nginx")

        logger.debug("Check that nginx flist works.")
        data = self.cont_client.system("/sandbox/bin/nginx -h").get()
        self.assertIn("Usage: nginx", data.stderr)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/205")
    def test004_lua(self):
        j.builders.web.lua.sandbox(**self.sandbox_args)
        self.deploy_flist_container("lua")
        data = self.cont_client.system("/sandbox/bin/lua -h").get()
        self.assertIn("Usage: lua", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/186")
    def test005_openresty(self):
        j.builders.web.openresty.sandbox(**self.sandbox_args)
        self.deploy_flist_container("openresty")
        data = self.cont_client.system("/sandbox/bin/resty -h")
        self.assertIn("Usage: /sandbox/bin/resty", data.stdout)

    def test006_etcd(self):
        j.builders.db.etcd.sandbox(**self.sandbox_args)
        self.deploy_flist_container("etcd")
        data = self.cont_client.system("/sandbox/bin/etcd -h").get()
        self.assertIn("--snapshot-count", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/201")
    def test007_coredns(self):
        j.builders.network.coredns.sandbox(**self.sandbox_args)
        self.deploy_flist_container("coredns")
        data = self.cont_client.system("/sandbox/bin/coredns -h").get()
        self.assertIn("Usage: ", data.stdout)

    def test008_docker(self):
        logger.debug("Run docker sandbox, should succeed and upload flist on hub.")
        j.builders.virtualization.docker.sandbox(**self.sandbox_args)

        logger.debug("Deploy container with uploaded zdb builder flist.")
        self.deploy_flist_container("docker")

        logger.debug("Check that docker flist works.")
        data = self.cont_client.system("/bin/sandbx/dockerd -h").get()
        self.assertIn("Usage: /sandbox/bin/dockerd", data.stdout)

    def test009_zdb(self):
        logger.debug("Run zdb sandbox, should succeed and upload flist on hub.")
        j.builders.db.zdb.sandbox(**self.sandbox_args)

        logger.debug("Deploy container with uploaded zdb builder flist.")
        self.deploy_flist_container("0-db")

        logger.debug("Check that zdb flist works by run zdb binary, should succeed. ")
        data = self.cont_client.system("/bin/sandbx/zdb -h").get()
        self.assertIn("Usage: /sandbox/bin/zdb", data.stdout)

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

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/657")
    def test013_minio(self):
        logger.debug("Run  minio sandbox, should succeed and upload flist on hub.")
        j.builders.storage.minio.sandbox(
            zhub_client=self.zhub,
            reset=True,
            flist_create=True,
            merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
        )

        logger.debug("Deploy container with uploaded minio builder flist.")
        self.deploy_flist_container("minio")

        logger.debug("Check that minio flist works by run zdb binary, should succeed. ")
        self.assertIn("Usage: minio", self.check_container_flist("/sandbox/bin/minio"))

