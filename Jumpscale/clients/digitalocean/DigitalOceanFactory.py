from Jumpscale import j
from .DigitalOcean import DigitalOcean

JSConfigBaseFactory = j.application.JSBaseConfigsClass


class PacketNetFactory(JSConfigBaseFactory):

    __jslocation__ = "j.clients.digitalocean"
    _CHILDCLASS = DigitalOcean

    def _init(self):
        self.connections = {}

    def install(self):
        try:
            import digitalocean
        except:
            j.builders.runtimes.python.pip_package_install("python-digitalocean")
            import digitalocean

    def test(self):
        """
        do:
        kosmos 'j.clients.digitalocean.test()'
        """
        self.install()
        if not self.main.token_:
            token = j.console.askString("digital ocean token")
            self.main.token_ = token
            self.main.save()
        c = self.get(name="main")

        client = c.client
        droplet, sshclient = c.droplet_create(delete=False)

        sshclient.apps.kosmos()

        self._log_info(c.droplets)
        self._log_info(c.digitalocean_images)
        self._log_info(c.digitalocean_sizes)
        self._log_info(c.digitalocean_regions)
        self._log_info(droplet.ip_address)

        j.shell()
