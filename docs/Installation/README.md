# Installation Instructions Jumpscale X

## Prerequisites

Before starting the installation to make sure to install the [prerequisites](/docs/Installation/install_prerequisites.md).

## Install Jumpscale X using docker

```bash
# TODO CHANGE BRANCH WITH MASTER (replace development_installer)
# get the jsx command (installer)
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development/install/jsx.py?$RANDOM > /tmp/jsx ; \
chmod +x /tmp/jsx; \
# install
/tmp/jsx container-install
```

The installer will ask you to provide a secret (and a couple of yes/no questions to which you answer yes).
If successfull, you will see something like:

```bash
install succesfull:
# if you use a container do:
jsx container-kosmos

```

The install script has built and started a docker container named `3bot` on your machine.

## To use Jumpscale X

To start JumpcaleX:

```bash
# get your kosmos shell (inside your 3bot container)
/tmp/jsx container-kosmos
```

Once kosmos is launched you will see this line:

```bash
JSX>
```

Congrats ! You may now use this jsx shell to manipulate the Jumpscale X library ! Follow these [steps](Installation/get_started.md) to go further in the use of Jumpscale.

If jsx is missing from your `/tmp` folder:

```bash
# get the jsx command
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development_installer/install/jsx.py?$RANDOM > /tmp/jsx ; \
chmod +x /tmp/jsx; \
# get your kosmos shell (inside your 3bot container)
/tmp/jsx container-kosmos
```

## jsx command help

```bash
#get more help of jsx command
/tmp/jsx --help
```

## OSX requirements

[see here OSX requirements specifics](/docs/Installation/install_prerequisites.md#osx)

## JSX

JSX is the main tool for working with a jumpscale deployment

- install
- export/import docker containers
- export BCDB data (coming soon)
- access the kosmos shell in container
- configure your local or container JSX

see [JSX](jsx.md) for more info

## More Info

- [more info about container install](install_docker.md)
- [install in local system (EXPERTS ONLY)](install_insystem.md)
- [more info about the JSX tool](jsx.md)
- [init the jumpscale code, can be required after pulling new code](generation.md)

## Get Installer from Code (experts)

is easy to develop on the installer

```bash
#create directory, make sure your user has full access to this director (can be a manual step)
mkdir -p /sandbox/code/github/threefoldtech
cd /sandbox/code/github/threefoldtech;
#if you have a permission denied add sudo at the beginning of the command
# then do a sudo chown -R $USER:$USER /sandbox
git clone git@github.com:threefoldtech/jumpscaleX.git; cd jumpscaleX;
git checkout development
git pull

#link the installer from tmp to the source directory, makes it easy for the rest of this tutorial
rm -f /tmp/jsx.py
rm -f /tmp/InstallTools.py;
ln -s /sandbox/code/github/threefoldtech/jumpscaleX/install/jsx.py /tmp/jsx;
ln -s /sandbox/code/github/threefoldtech/jumpscaleX/install/InstallTools.py /tmp/InstallTools.py
```
