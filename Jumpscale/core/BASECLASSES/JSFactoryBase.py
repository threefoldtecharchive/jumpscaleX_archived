from Jumpscale import j

from .JSBase import JSBase


class JSFactoryBase(JSBase):
    def __init__(self, parent=None, topclass=True, **kwargs):
        self._factories = {}

        JSBase.__init__(self, parent=parent, topclass=False)

        for kl in self.__class__._CHILDCLASSES:
            obj = kl(parent=self)
            # j.shell()
            if hasattr(kl, "_name"):
                name = kl._name
            else:
                name = kl.__name__
            self.__dict__[name] = obj
            self._factories[name] = obj

        if topclass:
            self._init()
            self._init2(**kwargs)

    def _class_init(self):

        if not hasattr(self.__class__, "_class_init_done"):

            if hasattr(self.__class__, "_CHILDCLASS"):
                self.__class__._CHILDCLASSES = [self.__class__._CHILDCLASS]

            if not hasattr(self.__class__, "_CHILDCLASSES"):
                raise RuntimeError("need _CHILDCLASSES as class property for:%s" % self)

            # always needs to be in this order at end
            JSBase._class_init(self)
            self.__class__.__objcat_name = "factory"

    def _obj_cache_reset(self):
        """
        make sure that all objects we remember inside are emptied
        :return:
        """
        JSBase._obj_cache_reset(self)
        for factory in self._factories.values():
            factory._obj_cache_reset()
