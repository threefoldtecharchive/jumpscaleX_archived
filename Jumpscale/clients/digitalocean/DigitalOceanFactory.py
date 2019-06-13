from Jumpscale import j
from .DigitalOcean import DigitalOcean

JSConfigBaseFactory = j.application.JSBaseConfigsClass


class PacketNetFactory(JSConfigBaseFactory):

    __jslocation__ = "j.clients.digitalocean"
    _CHILDCLASS = DigitalOcean

    def _init(self):
        self.connections = {}

    # def install(self):
    #     try:
    #         import digitalocean
    #     except:
    #         j.builders.runtimes.python.pip_package_install("python-digitalocean")
    #         import digitalocean

    def get_testvm_sshclient(self, delete=False):
        """
        do:
        kosmos 'j.clients.digitalocean.get_testvm_sshclient()'
        """
        if not self.main.token_:
            token = j.tools.console.askString("digital ocean token")
            self.main.token_ = token
            self.main.save()
        c = self.get(name="main")
        if j.clients.ssh.exists("do_test"):
            sshclient = j.clients.ssh.get("do_test")
            rc, out, err = sshclient.execute("ls /", showout=False, die=False)
            if rc > 0:
                droplet, sshclient = c.droplet_create(delete=delete)
        else:
            droplet, sshclient = c.droplet_create(delete=delete)
        return sshclient

    def test(self):
        """
        do:
        kosmos 'j.clients.digitalocean.test()'
        """
        if not self.main.token_:
            token = j.tools.console.askString("digital ocean token")
            self.main.token_ = token
            self.main.save()
        c = self.get(name="main")

        client = c.client
        droplet, sshclient = c.droplet_create(delete=True)

        e = sshclient.executor

        e.execute("ls /")

        # sshclient.apps.kosmos()

        self._log_info(c.droplets)
        self._log_info(c.digitalocean_images)
        self._log_info(c.digitalocean_sizes)
        self._log_info(c.digitalocean_regions)
        self._log_info(droplet.ip_address)
