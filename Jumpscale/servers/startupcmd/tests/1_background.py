from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="background")' --debug
    """

    self.http_back.delete()
    self.http_back.cmd_start = "python3 -m http.server"  # starts on port 8000
    self.http_back.monitor.ports = 8000
    self.http_back.executor = "background"
    self.http_back.timeout = 5
    self.http_back.start()
    assert self.http_back.pid
    assert self.http_back.is_running() == True
    self.http_back.stop()
    assert self.http_back.is_running() == False
    self.http_back.delete()

    self.http_back.delete()

    return "OK"
