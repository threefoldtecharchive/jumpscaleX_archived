# Installation Instructions Jumpscale X


```bash
#get the installer
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/master/install/jsx.py?$RANDOM > /tmp/jsx
chmod 777 /tmp/jsx
#install
/tmp/jsx container-install
#get first time your kosmos shell
/tmp/jsx container-kosmos
#get more help of jsx command
/tmp/jsx --help
```

before you can do this you need to make sure that docker has been installed on your system.

## To use

```bash
#to get container kosmos shell (JSX)
python3 /tmp/jsx.py container-kosmos
#to get shell of the ubuntu base os underneath in the container
python3 /tmp/jsx.py container-shell
```

## OSX requirements

```bash
#to install brew:
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# install requirements
brew install curl python3 git rsync
```

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
git checkout master
git pull

#link the installer from tmp to the source directory, makes it easy for the rest of this tutorial
rm -f /tmp/jsx.py
rm -f /tmp/InstallTools.py;
ln -s /sandbox/code/github/threefoldtech/jumpscaleX/install/jsx.py /tmp/jsx;
ln -s /sandbox/code/github/threefoldtech/jumpscaleX/install/InstallTools.py /tmp/InstallTools.py
```
