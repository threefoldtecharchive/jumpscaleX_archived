from Jumpscale import j
import traceback
import sys


def ssh():
    # j.clients.sshagent.test()  #should not do, because in container there will be no ssh-key loaded any more to continue the tests
    j.clients.sshkey.test()

def schema():
    j.data.schema.test()
    j.data.types.test()


def bcdb():
    j.tools.tmux.kill()
    assert len(j.tools.tmux.server.sessions) == 1
    j.servers.zdb.test(build=True)
    j.clients.zdb.test()
    j.data.bcdb.test()

def servers():
    if j.core.platformtype.myplatform.isUbuntu:
        j.builder.web.traefik.install()
        # j.builder.db.etcd.install()
        j.builder.network.coredns.install()

# ssh()
# schema()
# bcdb()
# servers()


j.data.bcdb.test()


