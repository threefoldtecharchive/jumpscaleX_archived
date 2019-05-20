import time
import pytest

from Jumpscale import j
from Jumpscale.sal.dnsmasq.Dnsmasq import DNSMasq


TEST_DNSMASQ = "/tmp/dnsmasq"


@pytest.mark.skip(reason="test need to be reviewed")
def test_main(self=None):
    systemd = j.sal.process.psfind("systemd-resolved")

    try:
        dns_masq = DNSMasq(TEST_DNSMASQ)

        # install and start dnsmasq
        dns_masq.install(start=False, device="lo")
        assert j.sal.fs.exists(dns_masq._configfile) is True
        if systemd:
            j.sal.process.execute("systemctl stop systemd-resolved")
        dns_masq.install(start=True, device="lo")
        time.sleep(5)
        cmd = j.tools.bash.get().cmd_path_get("dnsmasq")
        assert j.sal.process.psfind(cmd) is True

        # add host
        dns_masq.host_add("5E-A4-92-AB-2D-27", "127.0.0.1")
        assert j.sal.fs.exists(dns_masq._hosts) is True
        te = j.tools.code.text_editor_get(dns_masq._hosts)
        assert "5E-A4-92-AB-2D-27,127.0.0.1" in te.content

        # remove host
        dns_masq.host_remove("5E-A4-92-AB-2D-27")
        te = j.tools.code.text_editor_get(dns_masq._hosts)
        assert "5E-A4-92-AB-2D-27,127.0.0.1" not in te.content

        j.sal.process.killProcessByName(cmd)
    finally:
        if systemd:
            j.sal.process.execute("systemctl start systemd-resolved")
