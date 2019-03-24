from Jumpscale import j
import traceback
import sys

try:
    j.clients.zdb.test()
except Exception as e:
    sys.stderr.write('\nError In ZDB Client\n')
    traceback.print_exc()

try:
    j.data.bcdb.test()
except Exception as e:
    sys.stderr.write('\nError In BCDB\n')
    traceback.print_exc()

try:
    j.data.schema.test()
except Exception as e:
    sys.stderr.write('\nError In SCHEMA\n')
    traceback.print_exc()

try:
    j.servers.zdb.test()
except Exception as e:
    sys.stderr.write('\nError In ZDB Server\n')
    traceback.print_exc()

try:
    j.clients.sshagent.test()
except Exception as e:
    sys.stderr.write('\nError In SSHagent\n')
    traceback.print_exc()

try:
    j.clients.sshkey.test()
except Exception as e:
    sys.stderr.write('\nError In SSHKey\n')
    traceback.print_exc()