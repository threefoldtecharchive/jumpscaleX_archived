


## Configs Base class as singleton (only 1 instance)


```python

class CurrencyLayerFactory(j.application.JSBaseConfigsClass):

    _CHILDCLASS = CurrencyLayerSingleton


class CurrencyLayerSingleton(j.application.JSBaseConfigClass):

    __jslocation__ = 'j.clients.currencylayer'

    _SCHEMATEXT = """
    @url = jumpscale.currencylayer.client
    name* = "" (S)
    api_key_ = "" (S)
    """

    def __init__(self):
        factory = CurrencyLayerFactory() #get access to factory, then give to only child = singleton
        j.application.JSBaseConfigClass.__init__(self,name="main",factory=factory)

    def _init(self):
        #your initialization


```

the currency layer tool only needs 1 instance, as such it inherits from JSBaseConfigClass.

To make sure that there is only 1 instance we call the Baseclass with always name = "main", which will make sure we always have the same item.

