
# install

## easiest way

### OSX

required steps:

- install brew
- install requirements
- create the dir with right permissions
- install using the install script

```bash
#to install brew:
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# install requirements
brew install curl python3

#create dir
sudo mkdir -p /sandbox; sudo chown -R "${USER}:staff" /sandbox

#do the installation
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/master/install/install.py?$RANDOM > /tmp/install.py;python3 /tmp/install.py
```

### Ubuntu

#### Docker installation
```
git clone https://github.com/threefoldtech/jumpscaleX.git
cd jumpscaleX
sudo docker build --rm -t threefoldtech/jsx .
```

If you are a developer don't forget to load your SSH key for github.

## more info

see also [install/readme.md](../../install/README.md)

## with SSH key

should add your ssh key in your github account 

to see if SSL key has been loaded
```bash 
ssh-add -L
``` 

```bash
export USEGIT=1
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/master/install/install.py?$RANDOM > /tmp/install.py;python3 /tmp/install.py
```

there are some env variables which can be used
```
#makes sure that we use python & libraries from the system (in other words not the sandbox)
export INSYSTEM=1

#force not to use git, download with curl (if git not installed then it will automatically use curl)
export USEGIT=0

#if there are changes done in the code dir, and you are e.g. testing this installer you can use this env var to give a commit message
export GITMESSAGE=
```

- to use

```bash
source /sandbox/env.sh
js_shell
```

