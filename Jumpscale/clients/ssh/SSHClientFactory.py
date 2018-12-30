
from Jumpscale import j
from .SSHClient import SSHClient
from .SSHClientParamiko import SSHClientParamiko
from .SSHClientBase import  SSHClientBase

class SSHClientFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients.ssh"
    _CHILDCLASS = SSHClientBase

    def _init(self):
        self._clients = {}

    def _childclass_selector(self,dataobj,kwargs):
        """
        gives a creator of a factory the ability to change the type of child to be returned
        :return:
        """
        if j.core.platformtype.myplatform.isMac:
            return SSHClientParamiko
        else:
            return SSHClient

    def test(self):
        '''
        js_shell 'j.clients.ssh.test()'
        '''

        s=j.clients.ssh.instances.test
        s.addr="a.b.c.d"
        s.port=1053
        s.sshkey_name="test"

        j.clients.ssh.instances.test2.data_update(addr="a.b.c.e", port=1054, sshkey_name="test2", passwd="passwd")
        print (j.clients.ssh.instances.test2)

        assert j.clients.ssh.instances.test2.port == 1054


        #j.clients.ssh.instances.test2.shell()  #NOT TO BE DONE IN TEST but can use to do ssh
