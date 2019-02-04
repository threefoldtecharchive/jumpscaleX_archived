
from Jumpscale import j

class LoggerFactory(j.application.JSBaseClass):

    __jslocation__ = "j.tools.logger"
    # _CHILDCLASS = LoggerBase
    # _LoggerInstance = LoggerInstance


    @property
    def debug(self):
        return j.core.myenv.config["DEBUG"]

    @debug.setter
    def debug(self,value):
        assert j.data.types.bool(value)
        j.core.myenv.config["DEBUG"]=value
        j.core.myenv.config_save()
        self.reload()

    @property
    def config(self):
        res={}
        for name in j.core.myenv.config.keys():
            if name.startswith("LOGGER") or name=="DEBUG":
                res[name]=j.core.myenv.config[name]
        return res

    @debug.setter
    def config(self,value):
        """

        default :
            {'DEBUG': True,
            'LOGGER_INCLUDE': ['*'],
            'LOGGER_EXCLUDE': ['sal.fs'],
            'LOGGER_LEVEL': 15,
            'LOGGER_CONSOLE': False,
            'LOGGER_REDIS': True
            'LOGGER_REDIS_ADDR': None  #NOT USED YET, std on the core redis
            'LOGGER_REDIS_PORT': None
            'LOGGER_REDIS_SECRET': None
            }

        :param value: dict with config properties, can be all or some of the above
        :return:
        """
        assert j.data.types.dict(value)
        for name in j.core.myenv.config.keys():
            if name.startswith("LOGGER") or name=="DEBUG":
                if name in value:
                    j.core.myenv.config[name] = value[name]
        j.core.myenv.config_save()

    def reload(self):
        """
        kosmos 'j.tools.logger.reload()'
        will walk over jsbase classes & reload the logging config
        :return:
        """
        j.clients.ssh.a
        for obj in j.application._iterate_rootobj():
            obj._log_init(children=True)
            # self._print(obj._key)


    def test(self,name="base"):
        '''
        js_shell 'j.tools.logger.test()'
        '''
        self._test_run(name=name)
