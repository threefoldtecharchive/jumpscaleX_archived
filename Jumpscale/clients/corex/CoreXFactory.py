from Jumpscale import j
from .CoreXClient import CoreXClient


class CoreXClientFactory(j.application.JSBaseConfigsClass):

    __jslocation__ = "j.clients.corex"
    _CHILDCLASS = CoreXClient

    def _init(self):
        pass

    def corex_server_install(self):
        j.builders.apps.corex.install()

    def test(self):
        """
        kosmos 'j.clients.corex.test()'
        :return:
        """

        def test(passw=False):

            if passw:
                port = 7681
                cmd = "/sandbox/bin/corex --port {} -c user:pass".format(port)
            else:
                port = 7682
                cmd = "/sandbox/bin/corex --port {}".format(port)

            cmd0 = j.tools.startupcmd.get(name="corex_%s" % port, cmd=cmd, ports=[port])
            cmd0.start(reset=True)

            cl = self.get(name="test", addr="localhost", port=port)

            assert cl._process_list() == []

            r = cl.process_start("mc", "mc")

            # lets now see we can get the right objects back

            r2 = cl.process_get("mc")
            assert r.data.id == r2.data.id
            assert r.corex_id == r2.corex_id

            r2 = cl.process_get(id=r.data.id)
            assert r.data.id == r2.data.id
            assert r.corex_id == r2.corex_id

            r2 = cl.process_get(corex_id=r.corex_id)
            assert r.data.id == r2.data.id
            assert r.corex_id == r2.corex_id

            r2 = cl.process_get(pid=r.pid)
            assert r.data.id == r2.data.id
            assert r.corex_id == r2.corex_id

            # now we collected processes in multiple ways

            r.ui()

            # lets do the stop test
            r2.stop()

            assert r2.state == "stopping"  # IS ISSUE THERE SHOULD BE A HARDKILL !!!

            r3 = cl.process_start("ls", "ls /")
            print(r3.logs)
            assert r3.state == "ok"
            r3.refresh()
            assert r3.state == "stopped"

            r4 = cl.process_start("bash", "bash")
            r4.refresh()
            assert r4.state == "ok"
            r4.stop()
            r4.refresh()
            assert r4.state == "stopping"

            j.shell()

        test(False)
