import subprocess

from Jumpscale.sal.ubuntu.Ubuntu import Ubuntu
from Jumpscale import j
from unittest import  TestCase

class Test_Ubuntu(TestCase):
    def setUp(self):
        self.ubuntu = Ubuntu()

    def tearDown(self):
        pass

    def test001_uptime(self):
        with open('/proc/uptime') as f:
            data = f.read()
            uptime, _ = data.split(' ')

        self.assertAlmostEqual(uptime, self.ubuntu.uptime(), 1000)

    def test002_check(self):
        self.assertTrue(self.ubuntu.check())

    def test003_version_get(self):
        self.assertIn('Ubuntu', self.ubuntu.version_get()['DESCRIPTION'])

    def test004_apt_install_check(self):
        # if it fails, it will raise an error
        self.ubuntu.apt_install_check('iputils-ping', 'ping')

    def test005_apt_install_version(self):
        self.ubuntu.apt_install_version('wget', '1.19.4-1ubuntu2.1')
        rc, out, err = j.sal.process.execute('wget -V', useShell=True)
        self.assertIn('1.19.4', out)

    def test006_deb_install(self):
        j.sal.process.execute('wget http://security.ubuntu.com/ubuntu/pool/universe/t/tmuxp/python-tmuxp_1.3.1-1_all.deb')
        self.ubuntu.deb_install(path='python-tmuxp_1.3.1-1_all.deb')
        rc, out, err = j.sal.process.execute('dpkg -s python-tmuxp | grep Status')
        self.assertIn('install ok', out)

    def test007_pkg_list(self):
        self.assertNotEqual(self.ubuntu.pkg_list('ping'), 0)

    


