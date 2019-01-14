from Jumpscale import j

from .JSBase import JSBase

class JSFactoryBase(JSBase):


    def __init__(self):

        self._class_init() #is needed to init class properties, needs to be first thing

        self._obj_cache_reset()

        JSBase.__init__(self)
        self._init()

        self._logger_enable()

        for kl in self.__class__._CHILDCLASSES:
            obj=kl()
            self.__dict__[kl.__name__] = obj
            self._factories[kl.__name__] = obj

    def _class_init(self):


        if hasattr(self.__class__,"_CHILDCLASS"):
            self.__class__._CHILDCLASSES = [self.__class__._CHILDCLASS]

        if not hasattr(self.__class__,"_CHILDCLASSES"):
            raise RuntimeError("need _CHILDCLASSES as class property for:%s"%self)

        JSBase._class_init(self)


    def _obj_cache_reset(self):
        """
        make sure that all objects we remember inside are emptied
        :return:
        """
        JSBase._obj_cache_reset(self)
        for factory in self._factories.values():
            factory._obj_cache_reset(self)


