sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
export HOME=/root
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8zdb
export LC_ALL=en_US.UTF-8
. /sandbox/env.sh

cd /sandbox/code/github/threefoldtech/jumpscaleX
git pull
cd /sandbox/code/github/threefoldtech/digitalmeX
git pull
cd /sandbox/code/github/threefoldfoundation/info_foundation
git pull
cd /sandbox/code/github/threefoldfoundation/info_tokens
git pull
cd /sandbox/code/github/threefoldfoundation/lapis-wiki
git pull
jsx generate

#tmux new -d -s main  "export NACL_SECRET=123 ; kosmos 'j.servers.threebot.default.start()'"
kosmos --instruct /bot_configure.toml