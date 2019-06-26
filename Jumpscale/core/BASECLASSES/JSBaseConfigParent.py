# from Jumpscale import j
from .JSBaseConfig import JSBaseConfig
from .JSFactoryBase import JSFactoryBase


class JSBaseConfigParent(JSBaseConfig, JSFactoryBase):
    def __init__(self, data=None, parent=None, topclass=True, **kwargs):
        """
        :param data, is a jsxobject as result of jsX schema's
        :param factory, don't forget to specify this
        :param kwargs: will be updated in the self.data object

        the self.data object is a jsxobject (result of using the jsx schemas)

        """
        JSFactoryBase.__init__(self, topclass=False)
        JSBaseConfig.__init__(self, data=data, parent=parent, topclass=False, **kwargs)

        if topclass:
            self._init()
            self._init_pre(**kwargs)

    def __init_class(self):

        if not hasattr(self.__class__, "__init_class_done"):

            # always needs to be in this order at end
            JSFactoryBase.__init_class(self)
            JSBaseConfig.__init_class(self)
            self.__class__.__objcat_name = "factory_with_config"

    def _obj_cache_reset(self):
        """
        puts the object back to its basic state
        :return:
        """
        JSFactoryBase._obj_cache_reset(self)
        JSBaseConfig._obj_cache_reset(self)
