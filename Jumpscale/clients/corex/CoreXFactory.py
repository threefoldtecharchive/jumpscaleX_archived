from Jumpscale import j
from .CoreXClient import CoreXClient


class CoreXClientFactory(j.application.JSBaseConfigsClass):

    __jslocation__ = "j.clients.corex"
    _CHILDCLASS = CoreXClient

    def _init(self):
        pass

    def test(self):
        """
        kosmos 'j.clients.corex.test()'
        :return:
        """

        def test(passw=False):

            j.clients.corex.reset()

            s = j.servers.corex.default
            s.port = 8002

            if passw:
                s.user = "user"
                s.passwd = "pass"
                cl = self.get(name="test", addr="localhost", port=s.port, login="user", passwd_="pass")
            else:
                cl = self.get(name="test", addr="localhost", port=s.port)

            s.start()

            cl2 = s.client

            assert cl.process_list() == []

            j.shell()

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
            r.kill()
            r.refresh()
            assert r.state == "stopped"

            r3 = cl.process_start("ls", "ls /")
            print(r3.logs)
            assert r3.state == "ok"
            r3.refresh()
            assert r3.state == "stopped"

            cmd0.stop()
            j.data.corex_process.reset()
            j.clients.corex.reset()
            # j.shell()

        print("TEST NO AUTH")
        test(False)
        print("TEST WITH AUTH")
        test(True)
        print("ALL TEST OK")
