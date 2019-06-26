from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="corex")' --debug
    """

    j.servers.corex.default.check()
    corex = j.servers.corex.default.client

    self.http.executor = "corex"
    self.http.corex_client_name = corex.name
    self.http.timeout = 5
    self.http.delete()
    self.http.cmd_start = "python3 -m http.server"  # starts on port 8000
    self.http.executor = "corex"
    self.http.corex_client_name = corex.name
    self.http.start()

    self.http.monitor.ports = 8000

    j.shell()
    self.http.stop()
    self.http.delete()

    return "OK"
