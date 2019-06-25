from Jumpscale import j
from Jumpscale.builder.test.builder.base_test import BaseTest
import unittest
import time
from loguru import logger


class TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("sandbox_tests.log")
        logger.debug("Starting of sandbox testcases.")

    def test001_zbd(self):
        logger.debug("Zdb builder: run build method.")
        j.builders.db.zdb.build(reset=True)
        logger.debug("zdb builder: run install method.")
        j.builders.db.zdb.install()
        logger.debug("zdb builder: run start method.")
        j.builders.db.zdb.start()
        logger.debug("check that zdb server started successfully.")
        self.assertEqual(1, len(j.sal.process.getProcessPid("zdb")))
        logger.debug("zdb builder: run stop method.")
        j.builders.db.zdb.stop()
        logger.debug("check that zdb server stopped successfully.")
        self.assertEqual(0, len(j.sal.process.getProcessPid("zdb")))

    @unittest.skip("https://github.com/filebrowser/caddy/issues/32")
    def test002_caddy(self):
        j.builders.web.caddy.build(reset=True)
        j.builders.web.caddy.install()
        j.builders.web.caddy.start()
        self.assertEqual(1, len(j.sal.process.getProcessPid("caddy")))
        j.builders.web.caddy.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("caddy")))

    def test003_nginx(self):
        j.builders.web.nginx.build(reset=True)
        j.builders.web.nginx.install()
        j.builders.web.nginx.start()
        self.assertTrue(len(j.sal.process.getProcessPid("nginx")))
        j.builders.web.nginx.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("nginx")))

    def test004_traefik(self):
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

    def test005_minio(self):
        j.builders.storage.minio.build(reset=True)
        j.builders.storage.minio.install()
        j.builders.storage.minio.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("minio")))
        j.builders.storage.minio.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("minio")))

    def test006_golang(self):
        j.builders.runtimes.golang.build(reset=True)
        j.builders.runtimes.golang.install()
        self.assertTrue(j.builders.runtimes.golang.is_installed)

    def test007_lua(self):
        j.builders.runtimes.lua.build(reset=True)
        j.builders.runtimes.lua.install()
        try:
            j.sal.process.execute("which lua")
        except:
            self.assertTrue(False)
        j.builders.web.openresty.start()
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid("openresty")))
        j.builders.web.openresty.stop()
        time.sleep(10)
        self.assertEqual(0, len(j.sal.process.getProcessPid("openresty")))

    def test008_nimlang(self):
        j.builders.runtimes.nimlang.build(reset=True)
        j.builders.runtimes.nimlang.install()
        try:
            j.sal.process.execute("which nim")
        except:
            self.assertTrue(False)

    def test009_python(self):
        j.builders.runtimes.python.build(reset=True)
        j.builders.runtimes.python.install()
        try:
            j.sal.process.execute("which python")
        except:
            self.assertTrue(False)

    def test010_digitalme(self):
        j.builders.apps.digitalme.build(reset=True)
        j.builders.apps.digitalme.install()
        j.builders.apps.digitalme.start()
        self.assertTrue(len(j.sal.process.getProcessPid("openresty")))
        j.builders.apps.digitalme.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("openresty")))

    def test011_bitcoin(self):
        j.builders.blockchain.bitcoin.build(reset=True)
        j.builders.blockchain.bitcoin.install()
        j.builders.blockchain.bitcoin.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("bitcoind")))
        j.builders.blockchain.bitcoin.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("bitcoind")))

    def test012_ethereum(self):
        j.builders.blockchain.ethereum.build(reset=True)
        j.builders.blockchain.ethereum.install()
        j.builders.blockchain.ethereum.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("ethereum")))
        j.builders.blockchain.ethereum.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("ethereum")))

    def test013_etcd(self):
        j.builders.db.etcd.build(reset=True)
        j.builders.db.etcd.install()
        j.builders.db.etcd.start()
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid("etcd")))
        j.builders.db.etcd.stop()
        time.sleep(10)
        self.assertEqual(0, len(j.sal.process.getProcessPid("etcd")))

    def test014_capnp(self):
        j.builders.libs.capnp.build(reset=True)
        j.builders.libs.capnp.install()
        j.builders.libs.capnp.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("capnp")))
        j.builders.libs.capnp.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("capnp")))

    def test015_coredns(self):
        j.builders.network.coredns.build(reset=True)
        j.builders.network.coredns.install()
        j.builders.network.coredns.start()
        self.assertTrue(j.sal.process.getProcessPid("coredns"))
        j.builders.network.coredns.stop()
        time.sleep(10)
        self.assertFalse(j.sal.process.getProcessPid("coredns"))

    def test016_zerotier(self):
        j.builders.network.zerotier.build(reset=True)
        j.builders.network.zerotier.install()
        j.builders.network.zerotier.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("zerotier")))
        j.builders.network.zerotier.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("zerotier")))

    def test017_rust(self):
        j.builders.runtimes.rust.build(reset=True)
        j.builders.runtimes.rust.install()
        try:
            j.sal.process.execute("which rustup")
        except:
            self.assertTrue(False)

    def test018_redis(self):
        j.builders.db.redis.build(reset=True)
        j.builders.db.redis.install()
        j.builders.db.redis.start()
        self.assertEqual(2, len(j.sal.process.getProcessPid("redis-server")))
        j.builders.db.redis.stop()
        self.assertEqual(1, len(j.sal.process.getProcessPid("redis-server")))

    def test019_syncthing(self):
        j.builders.storage.syncthing.build(reset=True)
        j.builders.storage.syncthing.install()
        j.builders.storage.syncthing.start()
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid("syncthing")))
        j.builders.storage.syncthing.stop()
        time.sleep(10)
        self.assertEqual(0, len(j.sal.process.getProcessPid("syncthing")))

    def test020_freeflow(self):
        j.builders.apps.freeflow.build(reset=True)
        j.builders.apps.freeflow.install(reset=True)
        j.builders.apps.freeflow.start()
        self.assertTrue(len(j.sal.process.getProcessPid("apache2")))
        j.builders.apps.freeflow.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("apache2")))

    def test021_cmake(self):
        j.builders.libs.cmake.build(reset=True)
        j.builders.libs.cmake.install()
        try:
            j.sal.process.execute("which cmake")
        except:
            self.assertTrue(False)

    def test022_libffi(self):
        j.builders.libs.libffi.build(reset=True)
        j.builders.libs.libffi.install()
        try:
            j.sal.process.execute("which libtoolize")
        except:
            self.assertTrue(False)

    def test023_brotli(self):
        j.builders.libs.brotli.build(reset=True)
        j.builders.libs.brotli.install()
        try:
            j.sal.process.execute("which brotli")
        except:
            self.assertTrue(False)

    def test024_ardb(self):
        j.builders.db.ardb.build(reset=True)
        j.builders.db.ardb.install()
        j.builders.db.ardb.start()
        self.assertTrue(j.sal.process.getProcessPid("ardb"))
        j.builders.db.ardb.stop()
        self.assertFalse(j.sal.process.getProcessPid("ardb"))

    def test025_postgres(self):
        j.builders.db.postgres.build(reset=True)
        j.builders.db.postgres.install()
        j.builders.db.postgres.start()
        self.assertTrue(j.sal.process.getProcessPid("postgres"))
        j.builders.db.postgres.stop()
        self.assertFalse(j.sal.process.getProcessPid("postgres"))

    def test026_influx(self):
        j.builders.db.influxdb.build(reset=True)
        j.builders.db.influxdb.install()
        j.builders.db.influxdb.start()
        self.assertTrue(j.sal.process.getProcessPid("influx"))
        j.builders.db.influxdb.stop()
        self.assertFalse(j.sal.process.getProcessPid("influx"))

    def test027_php(self):
        j.builders.runtimes.php.build(reset=True)
        j.builders.runtimes.php.install()
        j.builders.runtimes.php.start()
        self.assertTrue(j.sal.process.getProcessPid("php-fpm"))
        j.builders.runtimes.php.stop()
        self.assertFalse(j.sal.process.getProcessPid("php-fpm"))

    def test028_docker(self):
        logger.debug("docker builder: run build method.")
        j.builders.virtualization.docker.build(reset=True)
        logger.debug("docker builder: run install method.")
        j.builders.virtualization.docker.install()
        logger.debug("docker builder: run start method.")
        j.builders.virtualization.docker.start()
        logger.debug("check that docker server started successfully.")
        self.assertTrue(j.sal.process.getProcessPid("containerd"))
        logger.debug("docker builder: run stop method.")
        j.builders.virtualization.docker.stop()
        logger.debug("check that docker server stopped successfully.")
        self.assertFalse(j.sal.process.getProcessPid("containerd"))
