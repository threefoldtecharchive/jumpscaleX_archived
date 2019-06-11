## JS Base Class

This is the baseclass used by most of the advanced baseclasses.

```
class JSBase:
    def __init__(self, parent=None, topclass=True, **kwargs):
        """
        :param parent: parent is object calling us
        :param topclass: if True means no-one inherits from us
        """
        self._parent = parent
        self._class_init()  # is needed to init class properties

        if topclass:
            self._init2(**kwargs)
            self._init()

        self._obj_cache_reset()
```

It contains all the logic that handles the `__jslocation__` property that attaches the class somewhere in the Jumpscale namespace. It also contais logic to control the [logger](readme.md#logging-on-a-jumpscale-object) and to inspect properties and methods on the parent class.

