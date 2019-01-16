
## Factory Base Class

can have a __jslocation__ means will be attached somewhere in the jumpscale namespace

it can optionally be a container for 1 or more config(s) classes
that is why its not _CHILDCLASS here but _CHILDCLASSES

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

the CHILDCLASSES are one or more config(s) classes

a childclass can be a singleton

