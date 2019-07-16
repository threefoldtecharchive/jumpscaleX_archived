from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="tmux")' --debug
    """

    self.http.delete()
    self.http.cmd_start = "python3 -m http.server"  # starts on port 8000
    self.http.monitor.ports = 8000
    self.http.start()
    assert self.http.pid
    self.http.timeout = 5
    assert self.http.is_running()
    self.http.stop()
    assert not self.http.is_running()

    self.http.delete()

    return "OK"
