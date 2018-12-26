**Master:**   
[![Build Status](https://travis-ci.com/threefoldtech/jumpscaleX.svg?branch=master)](https://travis-ci.com/threefoldtech/jumpscaleX)
[![codecov](https://codecov.io/gh/threefoldtech/jumpscaleX/branch/master/graph/badge.svg)](https://codecov.io/gh/threefoldtech/jumpscaleX)  
**Development:**  
[![Build Status](https://travis-ci.com/threefoldtech/jumpscaleX.svg?branch=development)](https://travis-ci.com/threefoldtech/jumpscaleX)
[![codecov](https://codecov.io/gh/threefoldtech/jumpscaleX/branch/development/graph/badge.svg)](https://codecov.io/gh/threefoldtech/jumpscaleX)

| asasd 	| sdfsdf 	| sdf 	|  	| dsfsdf 	|
|-------	|--------	|------	|---	|--------	|
|  	| asdf 	|  	|  	|  	|
|  	| asdf 	| adsf 	|  	| adf 	|
|  	| adf 	| adf 	|  	| adf 	|


this is a code block

```python
class Schema(j.application.JSBaseClass):
    def __init__(self, text):
        JSBASE.__init__(self)
        self.properties = []
        self._properties_list = []
        self.lists = []
        self._obj_class = None
        self._capnp = None
        self._index_list = None
        self.url = ""
        self._schema_from_text(text)
        self.key = j.core.text.strip_to_ascii_dense(self.url).replace(".", "_")
```

# Jumpscale

Jumpscale is a cloud automation product and a branch from what used to be 
Pylabs. About 9 years ago Pylabs was the basis of a cloud automation product 
which was acquired by SUN Microsystems from Q-Layer. In the mean time we are 
4 versions further and we have rebranded it to Jumpscale.

- [Jumpscale](#jumpscale)
  - [About Jumpscale Core](#about-jumpscale-core)
  - [Installing Jumpscale Core (NEW, need to test!!!)](#installing-jumpscale-core-new-need-to-test)
  - [Usage](#usage)
  - [Tutorials](#tutorials)
  - [Collaboration Conventions](#collaboration-conventions)

## About Jumpscale Core

The core module provides the bare framework into which other modules of Jumpscale plug into.

some tools

* [Config Manager](docs/config/configmanager.md)
  The config manager is a secure way to manage configuration instances.
  Anything saved to the file system is NACL encrypted and only decrypted on
  the fly when accessed.

- [Executors](docs/Internals/Executors.md)
  Jumpscale comes with its own executors that abstract working locally or
  remotely.  Of these executors:

  * SSH Executor (for remote execution)
  * Local Executor (for local execution)
  * Docker Executor (for executing on dockers)

## Installing Jumpscale Core (NEW, need to test!!!)

[see documentation](install/install.md)


## Usage

* The jsshell
  in your terminal, type `js_shell`

- In Python

  ```bash
  python3 -c 'from Jumpscale import j;print(j.application.getMemoryUsage())'
  ```

  the default mem usage < 23 MB and lazy loading of the modules.

## Tutorials

[Check Documentation](docs/howto/)


## Collaboration Conventions
[check conventions](docs/CONTRIBUTING.md)
