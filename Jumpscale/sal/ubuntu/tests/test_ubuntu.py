from Jumpscale.sal.ubuntu.Ubuntu import Ubuntu
from Jumpscale import j
from unittest import TestCase


class Test_Ubuntu(TestCase):
    j.sal.process.execute("apt-get install -y python3-distutils-extra python3-dbus python3-apt")

    def setUp(self):
        self.ubuntu = Ubuntu()

    def tearDown(self):
        pass

    def test001_uptime(self):
        with open("/proc/uptime") as f:
            data = f.read()
            uptime, _ = data.split(" ")

        self.assertAlmostEqual(float(uptime), self.ubuntu.uptime(), 1000)

    def test002_check(self):
        self.assertTrue(self.ubuntu.check())

    def test003_version_get(self):
        self.assertIn("Ubuntu", self.ubuntu.version_get())

    def test004_apt_install_check(self):
        # if it fails, it will raise an error
        self.ubuntu.apt_install_check("iputils-ping", "ping")

    def test005_apt_install_version(self):
        self.ubuntu.apt_install_version("wget", "1.19.4-1ubuntu2.2")
        rc, out, err = j.sal.process.execute("wget -V", useShell=True)
        self.assertIn("1.19.4", out)

    def test006_deb_install(self):
        j.sal.process.execute(
            "wget http://security.ubuntu.com/ubuntu/pool/universe/t/tmuxp/python-tmuxp_1.5.0a-1_all.deb"
        )
        self.ubuntu.deb_install(path="python-tmuxp_1.5.0a-1_all.deb")
        rc, out, err = j.sal.process.execute("dpkg -s python-tmuxp | grep Status", die=False)
        self.assertIn("install ok", out)

    def test007_pkg_list(self):
        self.assertEqual(len(self.ubuntu.pkg_list("ping")), 0)

    def test008_service_start(self):
        self.ubuntu.service_start("dbus")
        rc, out, err = j.sal.process.execute("service dbus status")
        self.assertIn("dbus is running", out)

    def test009_service_stop(self):
        j.sal.process.execute("service dbus start")
        self.ubuntu.service_stop("dbus")
        rc, out, err = j.sal.process.execute("service dbus status", die=False)
        self.assertIn("dbus is not running", out)

    def test010_service_restart(self):
        j.sal.process.execute("service dbus start")
        self.ubuntu.service_restart("dbus")
        rc, out, err = j.sal.process.execute("service dbus status")
        self.assertIn("dbus is running", out)

    def test011_service_status(self):
        j.sal.process.execute("service dbus start")
        self.assertTrue(self.ubuntu.service_status("dbus"))

    def test012_apt_find_all(self):
        self.assertIn("wget", self.ubuntu.apt_find_all("wget"))

    def test013_is_pkg_installed(self):
        self.assertTrue(self.ubuntu.is_pkg_installed("wget"))

    def test014_sshkey_generate(self):
        self.ubuntu.sshkey_generate(path="/tmp/id_rsa")
        rc, out, err = j.sal.process.execute("ls /tmp | grep id_rsa")
        self.assertIn("id_rsa", out)


def main(self=None):
    """
    to run:
    kosmos 'j.sal.ubuntu._test(name="ubuntu")'
    """
    test_ubuntu = Test_Ubuntu()
    test_ubuntu.setUp()
    test_ubuntu.test001_uptime()
    test_ubuntu.test002_check()
    test_ubuntu.test003_version_get()
    test_ubuntu.test004_apt_install_check()
    test_ubuntu.test005_apt_install_version()
    test_ubuntu.test006_deb_install()
    test_ubuntu.test007_pkg_list()
    test_ubuntu.test008_service_start()
    test_ubuntu.test009_service_stop()
    test_ubuntu.test010_service_restart()
    test_ubuntu.test011_service_status()
    test_ubuntu.test012_apt_find_all()
    test_ubuntu.test013_is_pkg_installed()
    test_ubuntu.test014_sshkey_generate()
    test_ubuntu.tearDown()
