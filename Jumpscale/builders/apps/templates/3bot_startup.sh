sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
export HOME=/root
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8zdb
export LC_ALL=en_US.UTF-8
. /sandbox/env.sh

# update all repos and checkout development_jumpscale branch
cd /sandbox/code/github/threefoldtech/jumpscaleX
git remote set-branches origin '*'
git stash; git fetch -v; git pull origin development_jumpscale; git checkout development_jumpscale -f
cd /sandbox/code/github/threefoldtech/digitalmeX
git remote set-branches origin '*'
git stash; git fetch -v; git pull origin development_jumpscale; git checkout development_jumpscale -f
cd /sandbox/code/github/threefoldfoundation/info_foundation
git pull
cd /sandbox/code/github/threefoldfoundation/info_tokens
git pull
cd /sandbox/code/github/threefoldfoundation/lapis-wiki
git pull
cd /sandbox/code/github/threefoldtech/digitalmeX
js_init generate
pip3 install peewee
cd /sandbox/code/github/threefoldtech/jumpscaleX
kosmos "j.servers.threebot.default.start()"