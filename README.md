[![Build Status](https://travis-ci.org/threefoldtech/jumpscale_core.svg?branch=development)](https://travis-ci.org/threefoldtech/jumpscale_core)

# Jumpscale

Jumpscale is a cloud automation product and a branch from what used to be 
Pylabs. About 9 years ago Pylabs was the basis of a cloud automation product 
which was acquired by SUN Microsystems from Q-Layer. In the mean time we are 
4 versions further and we have rebranded it to Jumpscale.

- [Jumpscale](#jumpscale)
  - [To Install](docs/Installation/install.md)
  - [Usage](#usage)
  - [Tutorials](#tutorials)

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

[see documentation](docs/Installation/install.md)


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
