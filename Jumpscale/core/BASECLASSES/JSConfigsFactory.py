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

        self._factories = {}

        if hasattr(self.__class__, "_CHILDCLASS"):
            # means we will only use 1 JSConfigs as child
            assert not hasattr(self.__class__, "_CHILDCLASSES")
            self.__class__._CHILDCLASSES = [self.__class__._CHILDCLASS]

        for kl in self.__class__._CHILDCLASSES:
            # childclasses are the JSConfigs classes
            obj = kl(parent=self)
            assert isinstance(obj, j.application.JSBaseConfigsClass) or isinstance(obj, j.application.JSBaseConfigClass)
            if hasattr(kl, "_name"):
                name = kl._name
            else:
                name = kl.__name__
            self._factories[name] = obj

    def _obj_cache_reset(self):
        """
        make sure that all objects we remember inside are emptied
        :return:
        """
        JSBase._obj_cache_reset(self)
        for factory in self._factories.values():
            factory._obj_cache_reset()

    def _bcdb_selector(self):
        """
        always uses the system BCDB, unless if this one implements something else
        """
        return j.application.bcdb_system

    def _members_names_get(self, filter=None):
        """
        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :param self:
        :param filter:
        :return:
        """

        def do():
            x = []
            for key, item in self._members.items():
                x.append(key)
            for item in self.findData():
                if item.name not in x:
                    x.append(item.name)

        x = self._cache.get(key="_members_names_get", method=do, expire=10)  # will redo every 10 sec
        return self._filter(filter=filter, llist=x, nameonly=True)

    def _members_get(self, filter=None):
        """
        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :return:
        """
        j.shell()
        x = []
        for key, item in self._members.items():
            x.append(item)
        for item in self.findData():
            if item not in x:
                x.append(item)
        return self._filter(filter=filter, llist=x, nameonly=False)

    def __getattr__(self, name):
        # if private then just return
        if (
            name.startswith("_")
            or name in self._methods_names_get()
            or name in self._properties_names_get()
            or name in self._dataprops_names_get()
        ):
            return self.__getattribute__(name)
        j.shell()
        w
        return r

    def __setattr__(self, key, value):
        self.__dict__[key] = value
