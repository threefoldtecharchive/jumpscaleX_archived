
# install

### should add your ssh key in your github account 
### to get your ssh key 
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

