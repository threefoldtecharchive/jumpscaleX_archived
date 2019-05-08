js_shell "j.clients.zdb.test()"
js_shell "j.data.bcdb.test()"
js_shell "j.data.schema.test()"
js_shell "j.servers.zdb.test()"
js_shell "j.clients.sshagent.test()"
js_shell "j.clients.sshkey.test()"
python3.6 -m pytest -v --ignore=/sandbox/code/github/threefoldtech/jumpscaleX/Jumpscale/builder/ /sandbox/code/github/threefoldtech/jumpscaleX
