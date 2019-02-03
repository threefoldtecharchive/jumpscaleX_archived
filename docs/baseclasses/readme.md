# base classes for JumpscaleX

## the lowest base class:

- [j.application.JSBaseClass](jsbase.md)

## the more advances ones:

- [j.application.JSFactoryBaseClass](factorybaseclass.md)
- [j.application.JSBaseConfigClass](config.md)
- [j.application.JSBaseConfigsClass](configs.md)

## special cases

- [singletons](config_singleton.md)

## properties available on all base classes


- _location  : e.g. j.clients.ssh, is always the location name of the highest parent 
- _name : name of the class itself in lowercase
- _logger_level: std 100, 100 means no logging, 0 is all logging
  - 10 means logs debugs and up
  - 15 means logs stdout & above, ...


### logging on a jumpscale object

- _logger_enable() will make sure self._logger_level = 0 (is for all classes related to self._location

- _log_debug : method to log a debug statement
- _print : print to stdout but also log
- _log_info : method to log a info statement
- _log_warning : method to log a warning statement
- _log_error : method to log an error statement
- _log_critical : method to log a critical statement

it will record the context for the log statements as

- self._location:self._name if self._name not in self._location


### how do baseclasses call each other

- the top class (who inherits from someone else)
    - is called with topclass=True in initator
- self.__init__() is called for each childclass, the most base class called first
- self._init() is called from the topclass only, meant to be implemented on topclass
- self._init2() is called from the topclass only, implemented on baseclasses, will call all child classes
    - the most base class is called last


### 

if you create your own classes who inherit from JSBase (which should be all)
use following patern

```python

class MyClass(JSBase):

    def _init(self):

        #your own initialization parts

```

do not implement your own __init__() !!!