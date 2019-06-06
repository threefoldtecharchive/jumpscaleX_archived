# Install JSX in system 

```
mkdir -p /sandbox/code/github/threefoldtech
cd /sandbox/code/github/threefoldtech;
#if you have a permission denied add sudo at the beginning of the command
# then do a sudo chown -R $USER:$USER /sandbox
git clone git@github.com:threefoldtech/jumpscaleX.git; cd jumpscaleX/install;

# with no sshagent
python3 jsx.py install --no_sshagent
```
## Note: Still in progress
see [../docs/Installation/install.md](../docs/Installation/install.md)
