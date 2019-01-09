from Jumpscale import j
from .Syncer import Syncer


class SyncerFactory(j.application.JSFactoryBaseClass):
    __jslocation__ = "j.tools.syncer"

    _CHILDCLASS = Syncer

    def _init(self):
        self.syncers = {}

    def get(self, name="default", sshclient_name="main", paths=None):
        """

        make sure there is an ssh client first, can be done by

            j.clients.ssh.get...

        :param name:
        :param ssh_client_name: name as used in j.clients.ssh
        :param paths: specified as
            e.g.  "{DIR_CODE}/github/threefoldtech/0-robot:{DIR_TEMP}/0-robot,..."
            e.g.  "{DIR_CODE}/github/threefoldtech/0-robot,..."
            can use the {} arguments
            if destination not specified then is same as source

        if not specified is:
            paths = "{DIR_CODE}/github/threefoldtech/jumpscaleX,{DIR_CODE}/github/threefoldtech/digitalmeX"

        :return:
        """
        if name not in self.syncers:
            if paths is None:
                paths = "{DIR_CODE}/github/threefoldtech/jumpscaleX,{DIR_CODE}/github/threefoldtech/digitalmeX"

            self.syncers[name] = super(SyncerFactory, self).get(name=name, sshclient_name=sshclient_name, paths=paths)
        return self.syncers[name]

    def sync(self):
        """
        execute to sync all syncers
        will push default code directories to remove ssh host
        """
        for name in self.syncers:
            self.syncers[name].sync()

    def test(self):
        """
        js_shell 'j.tools.syncer.test()'
        :return:
        """
        cl = j.clients.ssh.get(name="builder", addr="10.102.133.88", port=1053)
        r = cl.execute("ls / ")

        s = self.get(name="builder", sshclient_name=cl.name, paths=None)
        s.sync()
