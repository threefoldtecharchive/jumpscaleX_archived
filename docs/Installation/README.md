# Installation Instructions Jumpscale X
  
## Prerequisites
Before starting the installation make sure to go through the prerequisites. it differs according to your installation type

### Ubuntu

install requirements
```bash
apt install -y curl python3 python3-pip python3-click
```

### OSX

- os: `macOS 10.7 or newer`

install requirements
```bash
#to install brew (if not done yet):
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
#install components:
brew install curl python3 python3-pip python3-click
```

- see: [docker for mac installation](https://docs.docker.com/v17.12/docker-for-mac/install/#download-docker-for-mac)


### sshkey & ssh agent requirements

- install tools will automatically load ssh-agent if needed but if not use next instructions
- make sure to add your ssh-key to your github account's authenticated keys

if you want to manually launch ssh-agent:

```bash
eval `ssh-agent -s`
#if you don't have an ssh key yet
ssh-keygen
#if you have ssh-key
ssh-add
```

## Container Installation (recommended)

You will be asked to provide a secret and to authenticate github cloning in the middle of installation. make sure to add your ssh-key to your github account's authenticated keys

- 1- install the prerequisites
- 2- download the installation file, make it executable, then run it

```bash
# download
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development_jumpscale/install/jsx.py?$RANDOM > /tmp/jsx
# change permission
chmod +x /tmp/jsx
# install
/tmp/jsx container_install
```

## InSystem Install

Here we will install jumpscale using install option which willinstall jumpscale within your local system. 

- 1- install the prerequisites
- 2- download the installation file, make it executable, then run it

```bash
# download
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development_jumpscale/install/jsx.py?$RANDOM > /tmp/jsx
# change permission
chmod +x /tmp/jsx
# install
/tmp/jsx install 
```


## Extra options
also there's some more intersting options to use

#### interactivity

if you want to run interactive use options --no_interactive and options like -s mysecret
use help to learn more


#### reset

- Will restart the installation
```bash
/tmp/jsx install -r
```

#### delete
- if you are using a docker this option will delete the existing one
```bash
/tmp/jsx container_install -d
```

#### install with webcomponents
- installs webcomponents
```bash
/tmp/jsx container_install -w
```

#### jsx command help
- get more information about other options
```bash
#get more help of jsx command
/tmp/jsx --help
``` 

## Advanced Installation

it is easy to develop on the installer, will install from existing code on your system

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

## after-installation

### How to use Jumpscale X

To start JumpcaleX:
The install script has built and started a docker container named `3bot` on your machine.
```bash
# get your kosmos shell (inside your 3bot container)
/tmp/jsx container_kosmos
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
/tmp/jsx container_kosmos
```

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
- [see here OSX requirements specifics](/docs/Installation/install_prerequisites.md#osx)
