
from Jumpscale import j
import redis
from .ZDBClientBase import ZDBClientBase


class ZDBAdminClient(ZDBClientBase):
    def _init(self):
        """ is connection to ZDB

        port {[int} -- (default: 9900)
        mode -- user,seq(uential) see
                    https://github.com/rivine/0-db/blob/master/README.md
        """
        self.admin = True
        ZDBClientBase._init(self)

        self._system = None
        #
        if self.secret:
            # authentication should only happen in zdbadmin client
            self._log_debug("AUTH in namespace %s" % (self.nsname))
            self.redis.execute_command("AUTH", self.secret)

    def namespace_exists(self, name):
        try:
            self.redis.execute_command("NSINFO", name)
            # self._log_debug("namespace_exists:%s" % name)
            return True
        except Exception as e:
            if not "Namespace not found" in str(e):
                raise RuntimeError("could not check namespace:%s, error:%s" % (name, e))
            # self._log_debug("namespace_NOTexists:%s" % name)
            return False

    def namespaces_list(self):
        res = self.redis.execute_command("NSLIST")
        return [i.decode() for i in res]

    def namespace_new(self, name, secret="", maxsize=0, die=False):
        """
        check namespace exists & will return zdb client to that namespace

        :param name:
        :param secret:
        :param maxsize:
        :param die:
        :return:
        """
        self._log_debug("namespace_new:%s" % name)
        if self.namespace_exists(name):
            self._log_debug("namespace exists")
            if die:
                raise RuntimeError("namespace already exists:%s" % name)
            # now return std client
            return j.clients.zdb.client_get(addr=self.addr, port=self.port, mode=self.mode, secret=secret, nsname=name)

        self.redis.execute_command("NSNEW", name)
        if secret is not "":
            self._log_debug("set secret")
            self.redis.execute_command("NSSET", name, "password", secret)
            self.redis.execute_command("NSSET", name, "public", "no")

        if maxsize is not 0:
            self._log_debug("set maxsize")
            self.redis.execute_command("NSSET", name, "maxsize", maxsize)

        self._log_debug("connect client")

        ns = j.clients.zdb.client_get(addr=self.addr, port=self.port, mode=self.mode, secret=secret, nsname=name)

        assert ns.ping()

        return ns

    def namespace_get(self, name, secret=""):
        return self.namespace_new(name, secret)

    def namespace_delete(self, name):
        if self.namespace_exists(name):
            self._log_debug("namespace_delete:%s" % name)
            self.redis.execute_command("NSDEL", name)

    def reset(self, ignore=[]):
        """
        dangerous, will remove all namespaces & all data
        :param: list of namespace names not to reset
        :return:
        """
        for name in self.namespaces_list():
            if name not in ["default"] and name not in ignore:
                self.namespace_delete(name)
