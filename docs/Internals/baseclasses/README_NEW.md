# JSX Baseclasses

## Index
- [Intro](#intro)
- [Baseclasses](#base-classes)
    - [JSBase](#jsbase)
    - [JSAttr]()
    - [JSConfigsFactory]()
    - [JSConfigs]()
    - [JSConfig]()
- [How to use]()
- [Jumpscale generated]()
- [Examples]()

## Intro
In order to understand the jumpscaleX baseclasses we will take this simple example to figure out the hierarchy. BaseClasses are the parent of everything like config manager, clients, builders, servers .. etc.<br/>

Also they contain a lot of functions to help in logging, caching, auto completion in shell, config manager instance managment.

As we see in the following diagram [IPMI client](https://github.com/threefoldtech/jumpscaleX/tree/development_jumpscale/Jumpscale/clients/ipmi) 
![](images/baseclasses.png)

So if need to know how a client comes from:<br>
- The top parent class will be `JSBase` class.
- The factory (which has the base features for instances) inherits from `JSBaseConfigs` class and composes the client as a child class.
- The client (The instance) also inherits from `JSBaseConfig` <br/>

We will go through them in details the next parts

## Base Classes
### JSBase
This is the baseclass used by all other base classes, Its the lowest level one. Every object in Jumpscale inherits from this one.

### JSBase main functions
**1- Initialization of the class level** <br/>
    <p>walk to all parents, let them know that there are child classes, each child class has `__jslocation__` variable which defines it's location as a short path<br/>
    for example: `j.builders.db.zdb.build()`
    To execute this command db builders's dir has a factory class which has location variable `__jslocation__ = "j.builders.db"` also to point to all child classes. same goes with clients, servers, ..etc<br/>
    This is done in `__init_class` method</p>

**2- Logging** <br/>
    <p>All jumpscale logging methods and logic are implemented in JSBase.
    Logs have levels you can pass it as a parameter through `_logger_set()` method<br>
    param min_level if not set then will use the LOGGER_LEVEL from
    `sandbox/cfg/jumpscale_config.toml`,
    make sure that logging above minlevel will happen, std = 100
    if 100 means will not log anything <br/>
        - CRITICAL 	50 <br/>
        - ERROR 	40 <br/>
        - WARNING 	30 <br/>
        - INFO 	    20 <br/>
        - STDOUT 	15 <br/>
        - DEBUG 	10 <br/>
        - NOTSET 	0  <br/>
    if parents and children: will be set on all classes of the self.location e.g. j.clients.ssh (children, ...)
    if minlevel specified then it will always consider the logging to be enabled<br/>

__Logging Methods__<br/>
- `log()`: method takes whatever you want to log, also has a parameter log-level
- `_logging_enable_check`:  check if logging should be disabled for current js location
- `_logger_enable()`: will make sure self._logger_min_level = 0 (is for all classes related to self._location. <br/>
- `_log_debug` : method to log a debug statement. <br/>
- `_print` : print to stdout but also log. <br/>
- `_log_info` : method to log a info statement. <br/>
- `_log_warning` : method to log a warning statement. <br/>
- `_log_error` : method to log an error statement. <br/>
- `_log_critical` : method to log a critical statement. <br/>
</p>

**3- Caching logic** <br/>


**4- Logic for auto completion in shell** <br/>
- To make autocompeletion in kosmos shell, we need to know the children of each class and the methods or properties in it also the data if it contains, we will walk through the methods that do so.
- `__name_get`: Gets each name for instances in factory.
for example in `j.builders.db` it gets names in DBFactoryClass, zdb, mongo .. etc

- `_filter`: Check names to view only required once which means it won't show names starts with "_" or "__" unless you type it. It uses other methods as helpers like `_parent_name_get`, `_child_get` ..

- Output is shown through `__str__` method.

**5- State on execution of methods (the _done methods)** <br/>
- We can consider it as a flag to save the state of execting methods.
- `_done_set`: saves that this method had been executed so, it won't run again unless you change the state
also there are other methods in this arena; `_done_delete`, `_done_reset`,`_done_check`, `_done_key`

