
## Factory Base Class

Can have a `__jslocation__`, meaning it will be attached somewhere in the `Jumpscale` namespace.

It can optionally be a container for one or more config classes,
that is why it is not `_CHILDCLASS `here but `_CHILDCLASSES`.

```python
from Jumpscale import j

class World(j.application.JSFactoryBaseClass):
    """
    some text explaining what the class does
    """

    __jslocation__ = 'j.data.world'

    _CHILDCLASSES = [Cars,Ships]

    def _init(self):
        #this object properties to be set during initialization
        self.cars = Cars()
        self.ships = Ships()
```

The `_CHILDCLASSES` are one or more config(s) classes, always defined as a (Python) List.

A `childclass` can be a singleton.
