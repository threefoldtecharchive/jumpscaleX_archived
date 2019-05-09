sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
export HOME=/root
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
. /sandbox/env.sh

cp /sandbox/code/github/threefoldtech/digitalmeX/packages/init_bot/chatflows/bot_init.py /sandbox/code/github/threefoldtech/digitalmeX/DigitalMe/tools/openpublish/base_chatflows/
cp /sandbox/code/github/threefoldtech/digitalmeX/packages/init_bot/actors/userbot/userbot.py /sandbox/code/github/threefoldtech/digitalmeX/DigitalMe/tools/openpublish/base_actors/

rm -r /sandbox/cfg/nacl/*

kosmos --instruct /bot_nacl_configure.toml

# Start open_publish server to be able to talk to the chatflows
tmux new -d -s main  "kosmos 'j.tools.open_publish.default.servers_start()'"

# Wait for openpublish to start zdb
RETRY=15
while [ $RETRY -gt 0 ]
do
    echo >/dev/tcp/localhost/9900
    if [ $? -eq 0 ]
    then
        break
    else
        let RETRY-=1
        sleep 30
    fi
done


# Add instnace in model threebot.user.initialization to set the initialization token. This instance will be used by actor userbot to veryify the authenticity of the initialization request.
# Any change in the actor regarding namespace used should be reflected here
kosmos "bcdb = j.tools.open_publish.bcdb_get('threebotuser', use_zdb=True); bcdb.models_add('/sandbox/code/github/threefoldtech/digitalmeX/packages/init_bot/models'); model = bcdb.model_get('threebot.user.initialization'); model.new({'name': 'user_initialization', 'token': j.data.idgenerator.generateGUID()}).save()"
