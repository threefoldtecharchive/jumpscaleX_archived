
## base environment variables which can be used in a script

```
'DIR_BASE': '/sandbox',
'DIR_TEMP': '/tmp/jumpscale',
'DIR_VAR': '/sandbox/var',
'DIR_CODE': '/sandbox/code',
'USEGIT': True,
'INIT_DONE': False,
'SSH_AGENT': True,
'INSYSTEM': False,
'DIR_HOME': '/root'
```



## install a development sandbox

### add your ssh key to your ssh-agent
```bash 
ssh-add -L
``` 
## use git-based sandbox
```bash
export USEGIT=1
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/master/install/install.py?$RANDOM > /tmp/install.py;python3 /tmp/install.py
```


## install without git

```
#force not to use git, download with curl (if git not installed then it will automatically use curl)
export USEGIT=0

```

## to install on system
```
#makes sure that we use python & libraries from the system (in other words not the sandbox)
export INSYSTEM=1
```

## to use

```bash
source /sandbox/env.sh
js_shell
```

