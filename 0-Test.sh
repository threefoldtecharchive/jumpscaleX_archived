source /sandbox/env.sh; js_shell 'j.clients.zdb.test()'
source /sandbox/env.sh; js_shell 'j.data.bcdb.test()'
source /sandbox/env.sh; js_shell 'j.data.schema.test()'
source /sandbox/env.sh; js_shell 'j.servers.zdb.test()'
source /sandbox/env.sh; js_shell 'j.clients.sshagent.test()'
source /sandbox/env.sh; js_shell 'j.clients.sshkey.test()'
source /sandbox/env.sh; python3.6 -m pytest -v /sandbox/code/github/threefoldtech/jumpscaleX
