
# install

## easiest way

### OSX (without docker)

required steps:

- install brew
- install requirements
- create the dir with right permissions
- install using the install script

```bash
#to install brew:
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# install requirements

brew install curl python3 git rsync

#create dir
sudo mkdir -p /sandbox; sudo chown -R "${USER}:staff" /sandbox

#do the installation
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development_types/install/install.py?$RANDOM > /tmp/install.py;python3 /tmp/install.py
```

### Ubuntu (without docker)

On ubuntu should be very straight forward

```bash
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development_types/install/install.py?$RANDOM > /tmp/install.py;python3 /tmp/install.py
```

If you are a developer don't forget to load your SSH key for github.

## of you're a developer make sure you SSH key has been loaded

should add your ssh key in your github account 

to see if SSL key has been loaded
```bash 
ssh-add -L
``` 

## how to use non interactive 

```bash
python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py -h
```

```
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

e.g.

```
python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py 
```

### if you already have your code checked out you can use

```bash
python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py
```


## to use

```bash
source /sandbox/env.sh
js_shell
```

