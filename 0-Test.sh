source /sandbox/env.sh; js_shell 'j.clients.zdb.test()'
source /sandbox/env.sh; js_shell 'j.data.bcdb.test()'
source /sandbox/env.sh; js_shell 'j.data.schema.test()'
source /sandbox/env.sh; js_shell 'j.servers.zdb.test()'
source /sandbox/env.sh; js_shell 'j.clients.sshagent.test()'
source /sandbox/env.sh; js_shell 'j.clients.sshkey.test()'
source /sandbox/env.sh; pytest -v /sandbox/code/github/threefoldtech/jumpscaleX
source /sandbox/env.sh; js_init generate; cd /sandbox/code/github/threefoldtech/jumpscaleX/Jumpscale/builder/test/; nosetests-3.4 -vs --logging-level=WARNING test_cases.py --tc-file=config.ini --tc=itsyou.username:$IYO_USERNAME --tc=itsyou.client_id:$IYO_CLIENT_ID --tc=itsyou.client_secret:$IYO_CLIENT_SECRET --tc=zos_node.node_ip:$ZOS_NODE_IP
