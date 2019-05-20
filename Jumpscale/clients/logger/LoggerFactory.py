from Jumpscale import j
from .LoggerClient import LoggerClient


class LoggerFactory(j.application.JSBaseConfigsClass):

    __jslocation__ = "j.clients.logger"
    _CHILDCLASS = SSHClientBase

    def test(self, name="base"):
        """
        kosmos 'j.tools.logger.test()'
        """
        self._test_run(name=name)
