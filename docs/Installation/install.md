
# install

## Notes

JumpscaleX is meant to be run as root or inside a container. Therefore is you try to install from code you need to be logged as root ```sudo python install.py``` will not work.
The container image as a volume to the code on your local machine inside /sandbox/code. If you edit the code you can then test it inside the container.
* to debug use this line of python : ```"from pudb import set_trace; set_trace()"``` 
* to use a shell you can use ```j.shell()```


## Get Installer

### if you have nothing on your system, just get the installer

```bash
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/master/install/install.py?$RANDOM > /tmp/install.py

#if you want to use development branch (unstable) do:
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development/install/install.py?$RANDOM > /tmp/install.py
```

### if you want to work from code: for experts
#### this is also needed if you want to work with a docker file

```bash
#create directory, make sure your user has full access to this director (can be a manual step)
mkdir -p /sandbox/code/github/threefoldtech; cd /sandbox/code/github/threefoldtech;
#if you have a permission denied add sudo at the beginning of the command
# then do a sudo chown -R $USER:$USER /sandbox
git clone git@github.com:threefoldtech/jumpscaleX.git; cd jumpscaleX;
##if you want to work from unstable development branch uncomment next line
#git checkout development
#git pull

#link the installer from tmp to the source directory, makes it easy for the rest of this tutorial
rm -f /tmp/install.py; rm -f /tmp/InstallTools.py;
ln -s /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py /tmp/install.py;
ln -s /sandbox/code/github/threefoldtech/jumpscaleX/install/InstallTools.py /tmp/InstallTools.py
```

## Preparation

if **you're a developer** make sure you SSH key has been loaded
should add your ssh key in your github account 

to see if SSL key has been loaded
```bash 
ssh-add -L
``` 

This SSH key will be used in docker & non docker install.

## Installation

### Docker  (recommended)

- make sure docker installed
- only tested on Ubuntu & OSX

```bash
##RECOMMENDED
#will install in docker, delete if exists and starting from already created docker image (is faster)
python3 /tmp/install.py -3 -y -d --image=hub

#will install in docker, all answer yes but show the config params and allow to confirm the choices (so is safe)
python3 /tmp/install.py -3 -y -c

#will install in docker, all answer yes, will delete docker if it exists, will not ask to confirm choices
python3 /tmp/install.py -3 -y -d

#use interactive
python3 /tmp/install.py -3 -codepath=/sandbox/code

```
#### on OSX

- make sure /sandbox has been created (sudo was probably required and then you need to give yourself permission)
- in 'share' in docker preferences you need to add /sandbox otherwise you will get

```bash
docker: Error response from daemon: Mounts denied:
The path /sandbox/code
is not shared from OS X and is not known to Docker.
You can configure shared paths from Docker -> Preferences... -> File Sharing.
See https://docs.docker.com/docker-for-mac/osxfs/#namespaces for more info.
```

### Without Docker  (not recommended)

### Ubuntu

```bash
#interactive
python3 /tmp/install.py -1 

```

do the installation more unattended

```bash
#will install in system, all answer yes but show the config params and allow to confirm the choices (so is safe)
python3 /tmp/install.py -1 -y -c

```

One liner for ubuntu, without having to install the installer

```bash
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development/install/install.py?$RANDOM > /tmp/install.py;python3 /tmp/install.py
```


### OSX 

required steps:

- install brew
- create the dir with right permissions
- install using the install script

```bash
#to install brew:
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# install requirements

brew install curl python3 git rsync

#create dir
sudo mkdir -p /sandbox; sudo chown -R "${USER}:staff" /sandbox

#interactive
python3 /tmp/install.py -1 

```

do the installation more unattended

```bash
#will install in system, all answer yes but show the config params and allow to confirm the choices (so is safe)
python3 /tmp/install.py -1 -y -c

```


## help

```bash
python3 /tmp/install.py -h

Jumpscale X Installer
---------------------

# options

--reset : will remove everything (on OSX: brew, /sandbox) BECAREFULL
-h = this help

## type of installation

-1 = in system install
-2 = sandbox install
-3 = install in a docker (make sure docker is installed)
-w = install the wiki at the end, which includes openresty, lapis, lua, ...


## interactivity

-y = answer yes on every question (for unattended installs)
-c = will confirm all filled in questions at the end (useful when using -y)
-r = reinstall, basically means will try to re-do everything without removing (keep data)
--debug will launch the debugger if something goes wrong

## encryption

--secret = std is '1234', if you use 'SSH' then a secret will be derived from the SSH-Agent (only if only 1 ssh key loaded
--private_key = std is '' otherwise is 24 words, use '' around the private key
            if secret specified and private_key not then will ask in -y mode will autogenerate

## docker related

--name = name of docker, only relevant when docker option used
-d = if set will delete e.g. container if it exists (d=delete), otherwise will just use it if container install
--portrange = 1 is the default
              1 means 8100-8199 on host gets mapped to 8000-8099 in docker
              2 means 8200-8299 on host gets mapped to 8000-8099 in docker
--image=/path/to/image.tar or name of image (use docker images)
--port = port of container SSH std is 9022 (normally not needed to use because is in portrange:22 e.g. 9122 if portrange 1)

## code related

--codepath = "/sandbox/code" can overrule, is where the github code will be checked out
-p = pull code from git, if not specified will only pull if code directory does not exist yet
--branch = jumpscale branch: normally 'development'

```

## to use
### docker 
```bash
docker ps 
``` 
should output a running 3bot container   

you can then ssh into the container 
```bash
ssh root@localhost -A -p 9122 
```
and launch the REPL for JSX
```bash
source /sandbox/env.sh; kosmos
```

