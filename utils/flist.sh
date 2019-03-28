#!/bin/bash
set -ex

# make output directory
ARCHIVE=/tmp/archives
FLIST=/tmp/flist
mkdir -p $ARCHIVE

# install system deps
apt-get update
apt-get install -y curl unzip rsync locales git wget netcat tar sudo tmux ssh python3-pip redis-server libffi-dev python3-dev libssl-dev libpython3-dev libssh-dev libsnappy-dev build-essential pkg-config libvirt-dev libsqlite3-dev -y


# setting up locales
if ! grep -q ^en_US /etc/locale.gen; then
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
    locale-gen en_US.UTF-8
    echo "export LC_ALL=en_US.UTF-8" >> /root/.bashrc
    echo "export LANG=en_US.UTF-8" >> /root/.bashrc
    echo "export LANGUAGE=en_US.UTF-8" >> /root/.bashrc
    echo " export HOME=/sandbox" >> /root/.bashrc
    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8
    export LANGUAGE=en_US.UTF-8
fi

for target in /usr/local $HOME/opt $HOME/.ssh $HOME/opt/cfg $HOME/opt/bin $HOME/code $HOME/code/github $HOME/code/github/threefoldtech $HOME/code/github/threefoldtech/jumpscale_weblibs $HOME/opt/var/capnp $HOME/opt/var/log $HOME/jumpscale/cfg; do
    mkdir -p $target
    sudo chown -R $USER:$USER $target
done

pushd $HOME/code/github/threefoldtech

# cloning source code
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development/install/install.py?$RANDOM > /tmp/install.py;python3 /tmp/install.py 1 y y y y y

#ssh generate
ssh-keygen -f ~/.ssh/id_rsa -P ''
eval `ssh-agent -s`
ssh-add ~/.ssh/id_rsa
#change in permission
chown root:root /tmp
source /sandbox/env.sh 
cd /sandbox
js_shell "j.builder.runtimes.lua.install(reset=True)"
js_shell "j.tools.tmux.execute('source /sandbox/env.sh \n js_shell \'j.tools.markdowndocs.webserver()\'',window ='flist')"

echo "Waiting webserver to launch on 8080..."
while ! nc -z localhost 8080; do   
  sleep 10 # wait for 10 seconds before check again
done
js_shell "j.builder.runtimes.lua.lua_rocks_install() "

cd /sandbox 
echo """ sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
export HOME=/root
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
. /sandbox/env.sh
cd /sandbox/code/github/threefoldfoundation/info_foundation
git pull
cd /sandbox/code/github/threefoldfoundation/info_tokens
git pull
cd /sandbox/code/github/threefoldfoundation/lapis-wiki
git pull
rm -rf /sandbox/code/github/threefoldtech/jumpscaleX
cd  /sandbox/code/github/threefoldtech && git clone https://github.com/threefoldtech/jumpscaleX.git -b development
cd /sandbox/code/github/threefoldtech/jumpscaleX
git checkout f99f9af1948ac2bb4afccc3ca29bbeb953c2bd87
git cherry-pick f7c1e251cd4e087b7e8af7d5ad7ba4ec367edbaf
git cherry-pick 7cb987ed3e2f8e7867eb780efc9a2612bcb81abc

rm -rf /sandbox/code/github/threefoldtech/digitalmeX
cd  /sandbox/code/github/threefoldtech && git clone https://github.com/threefoldtech/digitalmeX.git -b development
cd /sandbox/code/github/threefoldtech/digitalmeX
git checkout c7599c9f59abe3a68038eacf9776aa3e2360d094
git cherry-pick a9ef0d31eaa4a632e8aa0d4f8192dd49d107b29b^..6f3547879b95bf3f9f321bad5485cf8333069b9e
git cherry-pick 8caf6e331b3c94cb9004a3da075b152768c39cdf^..4991397c679a44554b89160e993cfe82474168cd


ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/static/chat /sandbox/code/github/threefoldfoundation/lapis-wiki/static
ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/views/chat /sandbox/code/github/threefoldfoundation/lapis-wiki/views
ln -sf /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/applications/chat.moon /sandbox/code/github/threefoldfoundation/lapis-wiki/app.moon 

tmux new -d -s main  \" export NACL_SECRET=123 ; js_shell ' server = j.servers.gedis.configure(host=\\\"0.0.0.0\\\", port=8888) ; server.actor_add(\\\"/sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/actors/chatbot.py\\\"); server.chatbot.chatflows_load(\\\"/sandbox/code/github/threefoldtech/digitalmeX/packages/system/base/chatflows\\\"); server.start()' \"

js_shell \"j.tools.markdowndocs.webserver()\"
""" > 3bot_startup.sh

cd /sandbox
echo """ sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
export HOME=/root
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
. /sandbox/env.sh
cd /sandbox/code/github/threefoldfoundation/info_foundation
git pull
cd /sandbox/code/github/threefoldfoundation/info_tokens
git pull
cd /sandbox/code/github/threefoldfoundation/lapis-wiki
git pull
cd /sandbox/code/github/threefoldtech/digitalmeX
git pull


ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/static/chat /sandbox/code/github/threefoldfoundation/lapis-wiki/static
ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/views/chat /sandbox/code/github/threefoldfoundation/lapis-wiki/views
ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/system/chat/lapis/applications/chat.moon /sandbox/code/github/threefoldfoundation/lapis-wiki/app.moon 

tmux new -d -s main  \"export NACL_SECRET=123 ; js_shell 'j.builder.db.zdb.start(); zdb_cl = j.clients.zdb.client_admin_get(); zdb_cl = zdb_cl.namespace_new(\\\"notary_namespace\\\", secret=\\\"1234\\\"); bcdb = j.data.bcdb.new(zdbclient=zdb_cl, name=\\\"notary_bcdb\\\");bcdb.models_add(\\\"/sandbox/code/github/threefoldtech/digitalmeX/packages/notary/models \\\"); server = j.servers.gedis.configure(host=\\\"0.0.0.0\\\", port=8888);server.actor_add(\\\"/sandbox/code/github/threefoldtech/digitalmeX/packages/notary/actors/notary_actor.py\\\");server.models_add(models=bcdb.models.values());server.save();server.start()' \"

cd /sandbox/code/github/threefoldtech/digitalmeX/packages/notary
moonc . &&lapis server
""" > notary_startup.sh

cd /sandbox/code/github/threefoldtech/jumpscaleX/
cp utils/startup.toml /.startup.toml
tar -cpzf "/tmp/archives/JSX.tar.gz" --exclude dev --exclude sys --exclude proc  /
