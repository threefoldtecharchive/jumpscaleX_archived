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
        