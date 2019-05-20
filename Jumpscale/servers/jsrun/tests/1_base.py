from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.servers.jsrun.test(name="base")'

    """

    j.servers.jsrun.install()

    p = j.servers.jsrun.get(
        name="test",
        cmd="openresty",
        path="/tmp",
        env={"D": "1"},
        ports=[8081],
        stopcmd="openresty -s stop",
        process_strings=["nginx", "openresty"],
        reset=True,
    )
    p.start(reset=True)

    assert p.running

    assert j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=8081)

    p.stop()

    assert j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=8081) == False

    p2 = j.servers.jsrun.get(name="test")

    assert p2.running == False

    p2.start()

    assert j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=8081)

    p2.stop()

    assert p2.running == False

    self._log_info("OPENRESTY TEST DONE")

    return "OK"
