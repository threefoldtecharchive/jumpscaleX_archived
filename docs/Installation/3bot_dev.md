## Get Installer

### if you have nothing on your system, just get the installer

```bash
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/master/install/3bot_dev.py?$RANDOM > /tmp/3bot_dev.py

```

### if you want to work from code: for experts only

```bash
#create directory, make sure your user has full access to this director (can be a manual step)
mkdir -p /sandbox/code/github/threefoldtech
cd /sandbox/code/github/threefoldtech
git clone git@github.com:threefoldtech/jumpscaleX.git
cd jumpscaleX
##if you want to work from unstable development branch uncomment next line
#git checkout development
#git pull

#link the installer from tmp to the source directory, makes it easy for the rest of this tutorial
rm -f /tmp/3bot_dev.py
rm -f /tmp/InstallTools.py
ln -s /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py /tmp/3bot_dev.py
ln -s /sandbox/code/github/threefoldtech/jumpscaleX/install/InstallTools.py /tmp/InstallTools.py
```

## make sure you SSH key has been loaded

to see if SSL key has been loaded
```bash 
ssh-add -L
``` 

This SSH key will be used in the docker which runs the 3bot code

TODO:*1 link to more information to explain people how to create a key & load it in ssh-agent

if you're a developer: you should add your ssh key in your github account 


## install the 3bot development envjs_

```python
cd /tmp
#next options will answer yes on all defaults, start froms scratch (takes longer), delete container if it already exists
python3 3bot_dev.py install -s -d -y -c
```
to see more options do ```3bot_dev.py install -h```

## to connect to the 3bot

```python
python3 3bot_dev.py connect
```

## explore the other options

do ```3bot_dev.py -h```