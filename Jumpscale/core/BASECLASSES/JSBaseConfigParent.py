# from Jumpscale import j
from .JSBaseConfig import JSBaseConfig
from .JSFactoryBase import JSFactoryBase

class JSBaseConfigParent(JSBaseConfig,JSFactoryBase):


    def __init__(self,data=None, factory=None, **kwargs):
        """
        :param data, is a jsobject as result of jsX schema's
        :param factory, don't forget to specify this
        :param kwargs: will be updated in the self.data object

        the self.data object is a jsobject (result of using the jsx schemas)

        """
        JSFactoryBase.__init__(self)
        JSBaseConfig.__init__(self,data=data,factory=factory,**kwargs)


    def _class_init(self):
        JSFactoryBase._class_init(self)
        JSBaseConfig._class_init(self)


    def _obj_cache_reset(self):
        """
        puts the object back to its basic state
        :return:
        """
        JSFactoryBase._obj_cache_reset(self)
        JSBaseConfig._obj_cache_reset(self)

