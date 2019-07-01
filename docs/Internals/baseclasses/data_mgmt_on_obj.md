# data management on a class

## principles

Change the properties directly on the object

e.g.

```python
mysshclient = j.clients.ssh.a
mysshclient.addr = ...

```

## new vs existing data

when new object is created then property _isnew is set:

- kosmosobj._isnew = True

when class is instantiated then the caller of the object will call

- kosmosobj._init(**kwargs)
- kwargs are optional arguments which can be used to populate the obj data obj

above property can be used to check if data is new or not

## data_update method

- can be used to update data from dict or **kwargs.
- Will update the underlying object.
- Will not save.
- Will call trigger self._data_update()


## triggers

Triggers are defined on model level.

```def Trigger_add(self, method):```

will call the method as follows before doing a set in DB

- method(model,obj,kosmosinstance=None, action=None, propertyname=None)
- kosmosinstance only if _model used in an jumpscale configuration enabled class
- action is in "new, change, get,set_pre,set_post,delete"  done on DB layer
- propertyname only relevant for changes, is when object property gets changed e.g. ipaddr...

to add a custom Trigger on kosmos obj do

```
def mymethod(model,obj,kosmosinstance=None, action=None, propertyname=None):
    #do something e.g. manipulate the data model before storing in DB

kosmosobj._model.trigger_add(mymethod)
```






