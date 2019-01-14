


## Configs Base class as singleton (only 1 instance)


```python

class CurrencyTools(j.application.JSBaseConfigsClass):

    _CHILDCLASS = CurrencyTool

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

the currency layer tool only needs 1 instance, as such it inherits from JSBaseConfigClass.

To make sure that there is only 1 instance we call the Baseclass with always name = "main", which will make sure we always have the same item.

