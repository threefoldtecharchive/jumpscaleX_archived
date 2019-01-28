

# j.application.JSBaseConfigClass

Is the base class for a config object.

## init

```python
def __init__(self,data=None, factory=None, **kwargs):
    """
    :param data, is a jsobject as result of jsX schema's
    :param factory, don't forget to specify this
    :param kwargs: will be updated in the self.data object

    the self.data object is a jsobject (result of using the jsx schemas)

    """
```

## example

```python
class ZDBClientBase(j.application.JSBaseConfigClass):
    ...

class ZDBAdminClient(ZDBClientBase):
    def _init(self):
        """ 
        some desct
        """
        ZDBClientBase._init(self) #not always needed only when you inherit from a self defined class
        #do your initialization of you config class here

#to call
ZDBAdminClient(factory=self,addr=addr, port=port, secret=secret,mode=mode)
```

in this case we did not get a model object first,
we just passed the data as arguments to the init function and this will have created a `JSObject`` automatically.

