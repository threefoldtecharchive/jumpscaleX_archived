
from Jumpscale import j
from .SSHClient import SSHClient
from .SSHClientParamiko import SSHClientParamiko
from .SSHClientBase import SSHClientBase


class SSHClientFactory(j.application.JSBaseConfigsClass):

    __jslocation__ = "j.clients.ssh"
    _CHILDCLASS = SSHClientBase

    def _init(self):
        self._clients = {}

    def _childclass_selector(self,**kwargs):
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
        kosmos 'j.clients.ssh.test()'
        '''


        d = j.sal.docker.create(name='test', ports='22:8022', vols='', volsro='', stdout=True, base='phusion/baseimage',
                            nameserver=['8.8.8.8'], replace=True, cpu=None, mem=0,
                            myinit=True, sharecode=True)

        cl = j.clients.ssh.get(name="remote1",addr="188.166.116.127")


        s = j.clients.ssh.test2
        s.addr = "188.166.116.127"
        s.port = 1053
        s.sshkey_name = "test"

        j.clients.ssh.test2.data_update(addr="188.166.116.127", port=1054, sshkey_name="test2", passwd="passwd")
        print(j.clients.ssh.test2)

        assert j.clients.ssh.test2.port == 1054

        # j.clients.ssh.instances.test2.shell()  #NOT TO BE DONE IN TEST but can use to do ssh
