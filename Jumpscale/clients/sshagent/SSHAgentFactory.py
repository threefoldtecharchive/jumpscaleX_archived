from Jumpscale import j

from .SSHAgent import SSHAgent

JSConfigBase = j.application.JSFactoryBaseClass


class SSHAgentFactory(JSConfigBase):
    """
    """
    __jslocation__ = "j.clients.sshagent"
    _CHILDCLASS = SSHAgent
