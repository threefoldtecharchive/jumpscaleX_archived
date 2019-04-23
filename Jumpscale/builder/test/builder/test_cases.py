from Jumpscale import j
from Jumpscale.builder.test.flist.base_test import BaseTest
import unittest


class TestCases(BaseTest):
    def test001_zbd(self):
        j.builder.db.zdb.build(reset=True)
        j.builder.db.zdb.install()
        j.builder.db.zdb.start()
        self.assertEqual(1, len(j.sal.process.getProcessPid('zdb')))
        j.builder.db.zdb.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('zdb')))

    def test002_caddy(self):
        j.builder.web.caddy.build(reset=True)
        j.builder.web.caddy.install()
        j.builder.web.caddy.start()
        self.assertEqual(1, len(j.sal.process.getProcessPid('caddy')))
        j.builder.web.caddy.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('caddy')))

    def test003_nginx(self):
        j.builder.web.nginx.build(reset=True)
        j.builder.web.nginx.install()
        j.builder.web.nginx.start()
        self.assertEqual(1, len(j.sal.process.getProcessPid('nginx')))
        j.builder.web.caddy.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('nginx')))

    def test004_openresty(self):
        j.builder.web.openresty.build(reset=True)
        j.builder.web.openresty.install()
        j.builder.web.openresty.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('lapis')))
        j.builder.web.openresty.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('nginx')))

    def test005_traefik(self):
        j.builder.web.traefik.build(reset=True)
        j.builder.web.traefik.install()
        j.builder.web.traefik.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('traefik')))
        j.builder.web.traefik.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('traefik')))

    def test006_minio(self):
        j.builder.storage.minio.build(reset=True)
        j.builder.storage.minio.install()
        j.builder.storage.minio.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('minio')))
        j.builder.storage.minio.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('minio')))

    def test007_golang(self):
        j.builder.runtimes.golang.build(reset=True)
        j.builder.runtimes.golang.install()
        try:
            j.sal.process.execute('which go')
        except:
            self.assertTrue(False)

    def test008_lua(self):
        j.builder.runtimes.lua.build(reset=True)
        j.builder.runtimes.lua.install()
        try:
            j.sal.process.execute('which lua')
        except:
            self.assertTrue(False)

    def test008_nimlang(self):
        j.builder.runtimes.nimlang.build(reset=True)
        j.builder.runtimes.nimlang.install()
        try:
            j.sal.process.execute('which nim')
        except:
            self.assertTrue(False)

    def test009_python(self):
        j.builder.runtimes.python.build(reset=True)
        j.builder.runtimes.python.install()
        try:
            j.sal.process.execute('which python')
        except:
            self.assertTrue(False)

    def test010_digitalme(self):
        j.builder.apps.digitalme.build(reset=True)
        j.builder.apps.digitalme.install()
        j.builder.apps.digitalme.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('openresty'))
        j.builder.apps.digitalme.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('openresty'))

    def test011_bitcion(self):
        j.builder.blockchain.bitcoin.build(reset=True)
        j.builder.blockchain.bitcoin.install()
        j.builder.blockchain.bitcoin.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('bitcoin'))
        j.builder.blockchain.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('bitcoin'))

    def test012_ethereum(self):
        j.builder.blockchain.ethereum.build(reset=True)
        j.builder.blockchain.ethereum.install()
        j.builder.blockchain.ethereum.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('ethereum'))
        j.builder.blockchain.ethereum.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('ethereum'))
        
    
    def test013_etcd(self):
        j.builder.db.etcd.build(reset=True)
        j.builder.db.etcd.install()
        j.builder.db.etcd.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('etcd'))
        j.builder.db.etcd.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('etcd'))

    def test014_capnp(self):
        j.builder.libs.capnp.build(reset=True)
        j.builder.libs.capnp.install()
        j.builder.libs.capnp.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('capnp'))
        j.builder.libs.capnp.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('capnp'))

    def test015_coredns(self):
        j.builder.network.coredns.build(reset=True)
        j.builder.network.coredns.install()
        j.builder.network.coredns.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('coredns'))
        j.builder.network.coredns.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('coredns'))

    def test016_zerotier(self):
        j.builder.network.zerotier.build(reset=True)
        j.builder.network.zerotier.install()
        j.builder.network.zerotier.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('zerotier'))
        j.builder.network.zerotier.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('zerotier'))
        
    def test017_rust(self):
        j.builder.runtimes.rust.build(reset=True) 
        j.builder.runtimes.rust.install()
        try:
            j.sal.process.execute('which rust')        
        except:
            self.assertTrue(False)
    
    def test018_redis(self):

    def test019_syncthing(self):
        j.builder.storage.syncthing.build(reset=True)
        j.builder.storage.syncthing.install()
        j.builder.storage.syncthing.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid('syncthing'))
        j.builder.storage.syncthing.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid('syncthing'))

    def test020_caddyfilemanager(self):

    
