from paramiko.agent import AgentSSH, cSSH2_AGENTC_REQUEST_IDENTITIES, SSH2_AGENT_IDENTITIES_ANSWER, SSHException, AgentKey, Agent
from Jumpscale import j
JSBASE = j.application.JSBaseClass


class AgentSSHKeys(AgentSSH, JSBASE):
    """
    overrides key with no keyname
    """

    def __init__(self):
        if hasattr(self, "_conn") and self._conn is not None: # resource leak
            self._conn.close()
        self._conn = None
        self._keys = ()
        super().__init__()
        JSBASE.__init__(self)

    def get_keys(self):
        """
        Return the list of keys available through the SSH agent, if any.  If
        no SSH agent was running (or it couldn't be contacted), an empty list
        will be returned.

        :return:
            a tuple of `.AgentKey` objects representing keys available on the
            SSH agent
        """
        return self._keys

    def _connect(self, conn):
        self._conn = conn
        ptype, result = self._send_message(cSSH2_AGENTC_REQUEST_IDENTITIES)
        if ptype != SSH2_AGENT_IDENTITIES_ANSWER:
            raise SSHException('could not get keys from ssh-agent')
        keys = []
        for i in range(result.get_int()):
            keys.append(AgentKeyWithName(self, result.get_binary(), result.get_string()))
        self._keys = tuple(keys)


class AgentWithName(AgentSSHKeys, Agent):
    def __init__(self):
        AgentSSHKeys.__init__(self)
        super().__init__()


class AgentKeyWithName(AgentKey, JSBASE):
    """
    Private key held in a local SSH agent.  This type of key can be used for
    authenticating to a remote server (signing).  Most other key operations
    work as expected.
    """

    def __init__(self, agent, blob, keyname):
        self.keyname = keyname.decode()
        super().__init__(agent, blob)
        JSBASE.__init__(self)
