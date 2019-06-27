from Jumpscale import j
from Jumpscale.builder.test.builder.base_test import BaseTest
import unittest
import time
from loguru import logger


class TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("builder_tests_{time}.log")
        logger.debug("Starting of builder testcases  which test main methods:build,install,start and stop.")

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

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/654")
    def test002_caddy(self):
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

    def test003_nginx(self):
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

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/657")
    def test005_minio(self):
        logger.debug("minio builder: run build method.")
        j.builders.storage.minio.build(reset=True)
        logger.debug("minio builder: run build method.")
        j.builders.storage.minio.install()
        logger.debug("minio builder: run build method.")
        j.builders.storage.minio.start()
        logger.debug("check that minio server started successfully.")
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("minio")))
        logger.debug("minio builder: run build method.")
        j.builders.storage.minio.stop()
        logger.debug("check that minio server started successfully.")
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
        logger.debug("DigitalMe builder: run build method. ")
        j.builders.apps.digitalme.build(reset=True)
        logger.debug("DigitalMe builder: run install method. ")
        j.builders.apps.digitalme.install()
        logger.debug("DigitalMe builder: run start method. ")
        j.builders.apps.digitalme.start()
        logger.debug("check that DigitalMe builder is started successfully ")
        self.assertTrue(len(j.sal.process.getProcessPid("openresty")))
        logger.debug("DigitalMe builder: run stop method. ")
        j.builders.apps.digitalme.stop()
        logger.debug("check that DigitalMe builder is stopped successfully ")
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
        logger.debug("ETCD builder: run build method. ")
        j.builders.db.etcd.build(reset=True)
        logger.debug("ETCD builder: run install method. ")
        j.builders.db.etcd.install()
        logger.debug("ETCD builder: run start method. ")
        j.builders.db.etcd.start()
        time.sleep(10)
        logger.debug("check that etcd builder is started successfully. ")
        self.assertTrue(len(j.sal.process.getProcessPid("etcd")))
        logger.debug("ETCD builder: run stop method. ")
        j.builders.db.etcd.stop()
        time.sleep(10)
        logger.debug("check that etcd builder is stopped successfully. ")
        self.assertEqual(0, len(j.sal.process.getProcessPid("etcd")))

    def test014_capnp(self):
        logger.debug("capnp builder: run build method. ")
        j.builders.libs.capnp.build(reset=True)
        logger.debug("capnp builder: run install method. ")
        j.builders.libs.capnp.install()
        logger.debug("check that capnp builder is installed successfully. ")
        try:
            j.sal.process.execute("which capnp")
        except:
            self.assertTrue(False)

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
        logger.debug("Redis builder: run build method. ")
        j.builders.db.redis.build(reset=True)
        logger.debug("Redis builder: run install method. ")
        j.builders.db.redis.install()
        logger.debug("Redis builder: run start method. ")
        j.builders.db.redis.start()
        logger.debug("check that Redis builder is started successfully")
        self.assertEqual(2, len(j.sal.process.getProcessPid("redis-server")))
        logger.debug("Redis builder: run stop method. ")
        j.builders.db.redis.stop()
        logger.debug("check that Redis builder is stopped successfully")
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
        logger.debug("freeflow builder: run build method. ")
        j.builders.apps.freeflow.build(reset=True)
        logger.debug("freeflow builder: run install method. ")
        j.builders.apps.freeflow.install(reset=True)
        logger.debug("freeflow builder: run start method. ")
        j.builders.apps.freeflow.start()
        logger.debug("check that freeflow builder is started successfully")
        self.assertTrue(len(j.sal.process.getProcessPid("apache2")))
        logger.debug("freeflow builder: run stop method. ")
        j.builders.apps.freeflow.stop()
        logger.debug("check that freeflow builder is stopped successfully")
        self.assertEqual(0, len(j.sal.process.getProcessPid("apache2")))

    def test021_cmake(self):
        logger.debug("cmake builder: run build method.")
        j.builders.libs.cmake.build(reset=True)
        logger.debug("cmake builder: run install method.")
        j.builders.libs.cmake.install()
        try:
            logger.debug("check that cmake is installed successfully")
            j.sal.process.execute("which cmake")
        except:
            self.assertTrue(False)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/660")
    def test022_libffi(self):
        logger.debug("libffi builder: run build method.")
        j.builders.libs.libffi.build(reset=True)
        logger.debug("libffi builder: run install method.")
        j.builders.libs.libffi.install()
        try:
            logger.debug("check that libffi is installed successfully")
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
        logger.debug("ardb builder: run build method. ")
        j.builders.db.ardb.build(reset=True)
        logger.debug("ardb builder: run install method. ")
        j.builders.db.ardb.install()
        logger.debug("ardb builder: run start method. ")
        j.builders.db.ardb.start()
        logger.debug("check that ardb builder is started successfully. ")
        self.assertTrue(j.sal.process.getProcessPid("ardb"))
        logger.debug("ardb builder: run stop method. ")
        j.builders.db.ardb.stop()
        logger.debug("check that ardb builder is stopped successfully. ")
        self.assertFalse(j.sal.process.getProcessPid("ardb"))

    def test025_postgres(self):
        logger.debug("PostgresDB builder: run build method. ")
        j.builders.db.postgres.build(reset=True)
        logger.debug("PostgresDB builder: run install method. ")
        j.builders.db.postgres.install()
        logger.debug("PostgresDB builder: run start method. ")
        j.builders.db.postgres.start()
        logger.debug("check that postgres builder is started correctly")
        self.assertTrue(j.sal.process.getProcessPid("postgres"))
        logger.debug("PostgresDB builder: run stop method. ")
        j.builders.db.postgres.stop()
        logger.debug("check that postgres builder is stopped correctly")
        self.assertFalse(j.sal.process.getProcessPid("postgres"))

    def test026_influx(self):
        logger.debug("influxDB builder: run build method. ")
        j.builders.db.influxdb.build(reset=True)
        logger.debug("influxDB builder: run install method. ")
        j.builders.db.influxdb.install()
        logger.debug("influxDB builder: run start method. ")
        j.builders.db.influxdb.start()
        logger.debug("check that influxdb builder is started correctly")
        self.assertTrue(j.sal.process.getProcessPid("influx"))
        logger.debug("influxDB builder: run stop method. ")
        j.builders.db.influxdb.stop()
        logger.debug("check that influxdb builder is started correctly")
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

    def test028_mongodb(self):
        logger.debug("mongodb builder: run build method.")
        j.builders.db.mongodb.build(reset=True)
        logger.debug("mongodb builder: run install method.")
        j.builders.db.mongodb.install() 
        logger.debug("mongodb builder: run start method.")
        j.builders.db.mongodb.start()      
        logger.debug("check that mongodb started successfully.")
        self.assertTrue(j.sal.process.getProcessPid("mongod"))   
        logger.debug("mongodb builder: run stop method.")
        j.builders.db.mongodb.stop()
        logger.debug("check that mongodb stopped successfully.")
        self.assertFalse(j.sal.process.getProcessPid("mongod")) 

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/652")
    def test028_mariadb(self):
        j.builders.db.mariadb.build(reset=True)
        j.builders.db.mariadb.install()
        j.builders.db.mariadb.start()
        self.assertTrue(j.sal.process.getProcessPid("mysql"))
        j.builders.db.mariadb.stop()
        self.assertFalse(j.sal.process.getProcessPid("mysql"))

