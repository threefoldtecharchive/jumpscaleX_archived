from .Bash import  Bash
from Jumpscale import j



class BashFactory(j.application.JSBaseClass):

    __jslocation__ = "j.tools.bash"

    def _init(self):
        self._local = None
        self._sandbox = None

    @property
    def home(self):
        if not self._local:
            self._local = Bash()
        return self._local

    @property
    def sandbox(self):
        if not self._sandbox:
            self._sandbox = self.get(profile_path="/sandbox/env.sh")
        return self._sandbox

    def get(self, executor=None, profile_path=None):
        """
        if executor==None then will be local
        """
        return Bash(executor=executor,profile_path=profile_path)

    def test(self):
        """
        kosmos 'j.tools.bash.test()'
        :return:
        """

        bash = self.sandbox



