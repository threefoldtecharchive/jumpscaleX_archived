

## Factory Base Class

can have a __jslocation__ means will be attached somewhere in the jumpscale namespace


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




## Configs Base class as singleton (only 1 instance)


```python

class CurrencyTools(j.application.JSBaseConfigsClass):

    _CHILDCLASS = CurrencyTool


class CurrencyToolInstance(j.application.JSBaseConfigClass):


class CurrencyTool(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.currencylayer.client
    name* = "" (S)
    api_key_ = "" (S)
    """

    __jslocation__ = 'j.clients.currencylayer'

    def __init__(self):
        factory = CurrencyTools()
        j.application.JSBaseConfigClass(self,name="main",factory=factory)


```


```python
from Jumpscale import j

class World(j.application.JSFactoryBaseClass):
    """
    some text explaining what the class does
    """

    __jslocation__ = 'j.clients.currencylayer'


    _CHILDCLASSES = [Cars,Ships]

    def _init(self):
        #this object properties to be set during initialization
        self.cars = Cars()
        self.ships = Ships()


```


## Configs Base class (multiple instances with config info)

```python
from Jumpscale import j

class CurrencyLayer(j.application.JSFactoryBaseClass):
    """
    some text explaining what the class does
    """

    _SCHEMATEXT = """
    @url = jumpscale.currencylayer.client
    name* = "" (S)
    api_key_ = "" (S)
    """

    def _init(self):
        self._data_cur = {}
        self._id2cur = {}
        #this object properties to be set during initialization
```
