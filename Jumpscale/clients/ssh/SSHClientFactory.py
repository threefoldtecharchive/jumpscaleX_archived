
from Jumpscale import j
from .SSHClient import SSHClient
from .SSHClientParamiko import SSHClientParamiko

class SSHClientFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients.ssh"

    def _init(self):
        self._clients = {}

    def get(self, name="main", **kwargs):
        """
        Get an instance of the SSHClient

        kwargs:
            name* = ""
            addr = ""
            port = 22
            addr_priv = ""
            port_priv = 22
            login = ""
            passwd = ""
            sshkey_name = ""
            clienttype = ""
            proxy = ""
            timeout = 60
            forward_agent = true
            allow_agent = true
            stdout = true

        """
        if name in self._clients:
            return self._clients[name]

        # cl = SSHClient(name=name)

        if j.core.platformtype.myplatform.isMac:
            use_paramiko = True
            cl = SSHClientParamiko(name=name)
        # elif use_paramiko is True:
        #     cl = SSHClientParamiko(name=instance,data=data)
        else:
            cl = SSHClient(name=name)

        cl.data_update(**kwargs)
        cl.allow_agent = True  #weird why I have to set this, should be default, need to check schema
        cl.forward_agent = True
        self._clients[name] = cl

        return cl


    def test(self, reset=False):
        '''
        js_shell 'j.clients.ssh.test()'
        '''

        #TODO: need to test, test that SSH-agent is being used
        self.get("test",addr="a.b.c.d", port=1053,sshkey_name="test")
        self.get("test2",addr="a.b.c.e", port=1054, sshkey_name="test2", passwd="passwd")
        #will have to change test later to start a local zos and test against that one
