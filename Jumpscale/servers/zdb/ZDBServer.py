from Jumpscale import j

JSBASE = j.application.JSBaseClass
import socket


# DO NEVER USE CONFIG MANAGEMENT CLASSES
class ZDBServer(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.servers.zdb"
        JSBASE.__init__(self)
        self.configure()
        #

    def configure(self, name="main", addr="127.0.0.1", port=9900, datadir="", mode="seq", adminsecret="123456"):
        self.name = name
        self.addr = addr
        self.port = port
        self.mode = mode
        self.adminsecret = adminsecret

    def isrunning(self):
        idir = "%s/index/" % (self.datadir)
        ddir = "%s/data/" % (self.datadir)
        if not j.sal.fs.exists(idir):
            return False
        if not j.sal.fs.exists(ddir):
            return False
        if not j.sal.nettools.tcpPortConnectionTest(self.addr, self.port):
            return False
        try:
            cl = self.client_admin_get()
            return cl.ping()
        except Exception as e:
            j.shell()

    def start(self, destroydata=False):
        """
        start zdb in tmux using this directory (use prefab)
        will only start when the server is not life yet

        kosmos 'j.servers.zdb.start()'

        """

        if not destroydata and j.sal.nettools.tcpPortConnectionTest(self.addr, self.port):
            r = j.clients.redis.get(ipaddr=self.addr, port=self.port)
            r.ping()
            return ()

        if destroydata:
            self.destroy()

        self.startupcmd.start()

        self._log_info("waiting for zdb server to start on (%s:%s)" % (self.addr, self.port))

        res = j.sal.nettools.waitConnectionTest(self.addr, self.port)
        if res is False:
            raise RuntimeError("could not start zdb:'%s' (%s:%s)" % (self.name, self.addr, self.port))

        self.client_admin_get()  # should also do a test, so we know if we can't connect

    def stop(self):
        self._log_info("stop zdb")
        self.startupcmd.stop()

    @property
    def startupcmd(self):

        idir = "%s/index/" % (self.datadir)
        ddir = "%s/data/" % (self.datadir)
        j.sal.fs.createDir(idir)
        j.sal.fs.createDir(ddir)

        # zdb doesn't understand hostname
        addr = socket.gethostbyname(self.addr)

        cmd = "zdb --listen %s --port %s --index %s --data %s --mode %s --admin %s --protect" % (
            addr,
            self.port,
            idir,
            ddir,
            self.mode,
            self.adminsecret,
        )
        return j.servers.startupcmd.get(name="zdb", cmd=cmd, path="/tmp", ports=[self.port])

        # tmux_window = "digitalme"
        # tmux_panel = "p13"
        #
        # j.tools.tmux.window_digitalme_get()
        # return j.tools.tmux.cmd_get(name="zdb_%s"%self.name,
        #             window_name=tmux_window,pane_name=tmux_panel,
        #             cmd=cmd,path="/tmp",ports=[self.port],
        #             process_strings = ["wwwww:"])

    def destroy(self):
        self.stop()
        self._log_info("destroy zdb")
        j.sal.fs.remove(self.datadir)
        # ipath = self.datadir+ "bcdbindex.db" % self.name

    @property
    def datadir(self):
        return "/sandbox/var/zdb/%s/" % self.name

    def client_admin_get(self, name="test"):
        """

        """
        cl = j.clients.zdb.client_admin_get(addr=self.addr, port=self.port, secret=self.adminsecret, mode=self.mode)
        return cl

    def client_get(self, nsname="default", secret="1234"):
        """
        get client to zdb

        """
        cl = j.clients.zdb.client_get(nsname=nsname, addr=self.addr, port=self.port, secret=secret, mode=self.mode)

        assert cl.ping()

        return cl

    def start_test_instance(self, destroydata=True, namespaces=[], admin_secret="123456", namespaces_secret="1234"):
        """

        kosmos 'j.servers.zdb.start_test_instance(reset=True)'

        start a test instance with self.adminsecret 123456
        will use port 9901
        and name = test

        production is using other ports and other secret

        :return:
        """
        self.name = "test"
        self.port = 9901
        self.mode = "seq"
        self.adminsecret = admin_secret
        self.tmux_panel = "p11"

        self.start()

        cla = self.client_admin_get()
        if destroydata:
            j.clients.redis._cache_clear()  # make sure all redis connections gone

        for ns in namespaces:
            if not cla.namespace_exists(ns):
                cla.namespace_new(ns, secret=namespaces_secret)
            else:
                if destroydata:
                    cla.namespace_delete(ns)
                    cla.namespace_new(ns, secret=namespaces_secret)

        if destroydata:
            j.clients.redis._cache_clear()  # make sure all redis connections gone

        return self.client_admin_get()

    def build(self, reset=True):
        """
        kosmos 'j.servers.zdb.build()'
        """
        j.builders.db.zdb.install(reset=reset)

    def test(self, build=False):
        """
        kosmos 'j.servers.zdb.test(build=True)'
        """
        self.destroy()
        if build:
            self.build()
        self.start_test_instance(namespaces=["test"])
        self.stop()
        self.start()
        cl = self.client_get(nsname="test")

        print("TEST OK")
