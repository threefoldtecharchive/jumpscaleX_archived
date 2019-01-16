

# j.application.JSBaseConfigClass

is the base class for a config object 

## init

```python3
def __init__(self,data=None, factory=None, **kwargs):
    """
    :param data, is a jsobject as result of jsX schema's
    :param factory, don't forget to specify this
    :param kwargs: will be updated in the self.data object

    the self.data object is a jsobject (result of using the jsx schemas)

    """
```



## example

```python3

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

in this case we did not get a model obj first, we just passed the daa as arguments to the init function & this will have created a jsobject automatically.

