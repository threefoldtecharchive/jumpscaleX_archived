from .Bash import  Bash
from Jumpscale import j



class BashFactory(j.application.JSBaseClass):

    __jslocation__ = "j.tools.bash"

    def _init(self):
        self._home = None
        self._sandbox = None

    @property
    def home(self):
        if not self._home:
            self._home = Bash()
        return self._home

    @property
    def sandbox(self):
        if not self._sandbox:
            self._sandbox = self.get("/sandbox")
        return self._sandbox

    def get(self,path=None, profile_name=None, executor=None):
        """

        :param path: if None then will be '~' = Home dir
        :param executor:
        :param profile_name: if None will look for env.sh, .bash_profile, .bashrc,  .profile in this order
        :return:
        """
        return Bash(executor=executor,path=path,profile_name=profile_name)

    def test(self):
        """
        kosmos 'j.tools.bash.test()'
        :return:
        """

        bash = self.get(profile_path="/tmp/env.sh")
        p = bash.profile
        p.delete()

        assert p.paths == ['/sandbox/bin', '/usr/local/bin', '/usr/bin']

        p.path_add("/tmp/1/",check_exists=False)
        assert p.paths == ["/tmp/1", '/sandbox/bin', '/usr/local/bin', '/usr/bin']
        p.path_add("/tmp/1/",check_exists=False)
        assert p.paths == ["/tmp/1", '/sandbox/bin', '/usr/local/bin', '/usr/bin']
        p.path_add("/tmp/2",end=True,check_exists=False)
        assert p.paths == ['/tmp/1', '/sandbox/bin', '/usr/local/bin', '/usr/bin', '/tmp/2']

        assert p.env == {'PATH': '/tmp/1:/sandbox/bin:/usr/local/bin:/usr/bin:/tmp/2'}

        p.path_delete("/tmp/1")

        assert p.env == {'PATH': '/sandbox/bin:/usr/local/bin:/usr/bin:/tmp/2'}

        p.env_set_part("TEST","A",1)

        p.env_set_part("TEST","A")
        p.env_set_part("TEST","B")

        assert p.env == {'PATH': '/sandbox/bin:/usr/local/bin:/usr/bin:/tmp/2', 'TEST': 'B:A'}

        self._log_info ("TEST FOR j.tools.bash is OK")



