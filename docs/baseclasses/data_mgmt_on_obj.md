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

### actions

- new is called when object created from model.new() method, not related to DB action, is only in mem
- change gets called when a property of the obj gets changed
- get is called after the model is populated from data from DB
- set_pre is called when object ready to be stored in DB but before
- set_post once indexing & storing in DB was succesful
- delete is called before removing from DB, when error in this step, deletion will not happen !


### example how to use

```python

class SomeClass(...):

    def _init(self,**kwargs):

        self._model.trigger_add(self._data_update_color)

    @staticmethod
    def _data_update_color(model,obj,kosmosinstance=None, action=None, propertyname=None):
        self = kosmosinstance  #this way code is same and can manipulate self like in other methods
        if propertyname=="color":
            j.shell()


o = SomeClass()
o.color = "red"
#this will now triger the _data_update_color method & because propertyname matches it will get in shell

easiest to add as staticmethod, that way its part of the class


```






