
from Jumpscale import j
from .LoggerBase import LoggerBase
from .LoggerInstance import  LoggerInstance

class LoggerFactory(j.application.JSBaseConfigsClass):

    __jslocation__ = "j.tools.logger"
    _CHILDCLASS = LoggerBase
    _LoggerInstance = LoggerInstance


    def test(self,name="base"):
        '''
        js_shell 'j.tools.logger.test()'
        '''
        self._test_run(name=name)
