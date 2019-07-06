# is a factory for multiple JSConfig baseclasses
from Jumpscale import j
from .JSBase import JSBase

"""
factory for JSConfig & JSConfigs objects
"""


class JSConfigsFactory(JSBase):
    def __init_class_post(self):

        if not hasattr(self.__class__, "_CHILDCLASSES"):
            raise RuntimeError("_CHILDCLASSES needs to be specified")

    def _init_pre(self, **kwargs):

        if hasattr(self.__class__, "_CHILDCLASS"):
            # means we will only use 1 JSConfigs as child
            assert not hasattr(self.__class__, "_CHILDCLASSES")
            self.__class__._CHILDCLASSES = [self.__class__._CHILDCLASS]

        for kl in self.__class__._CHILDCLASSES:
            # childclasses are the JSConfigs classes
            name = str(kl).split(".")[-1].split("'", 1)[0].lower()  # wonder if there is no better way
            if issubclass(kl, j.application.JSBaseConfigClass):
                obj = kl(parent=self, name=name)
                assert obj._parent
            elif issubclass(kl, j.application.JSBaseConfigsClass):
                obj = kl(parent=self, name=name)
                assert obj._parent
            else:
                raise RuntimeError("wrong childclass:%s" % kl)
            self._children[name] = obj

    def _init_post(self, **kwargs):
        self._protected = True

    def _obj_cache_reset(self):
        """
        make sure that all objects we remember inside are emptied
        :return:
        """
        JSBase._obj_cache_reset(self)
        for factory in self._children.values():
            factory._obj_cache_reset()

    def _bcdb_selector(self):
        """
        always uses the system BCDB, unless if this one implements something else
        """
        return j.application.bcdb_system

    def delete(self):
        for item in self._children_recursive_get():
            if isinstance(item, j.application.JSBaseConfigClass):
                self._log("delete:%s" % item.name)
                item.delete()

    def save(self):
        for item in self._children_recursive_get():
            if isinstance(item, j.application.JSBaseConfigClass):
                self._log("save:%s" % item.name)
                item.save()

    def __getattr__(self, name):
        # if private then just return
        if name in self._children:
            return self._children[name]
        return self.__getattribute__(name)

    def __setattr__(self, key, value):
        if key in ["_protected"]:
            self.__dict__[key] = value
        elif not self._protected or key in self._properties:
            self.__dict__[key] = value
        else:
            raise RuntimeError("protected property:%s" % key)
