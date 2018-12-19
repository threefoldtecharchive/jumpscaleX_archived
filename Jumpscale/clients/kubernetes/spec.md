```python
from Jumpscale import j

# pip install kube


class KubernetesFactory:

    def __init__(self):
        self.__jslocation__ = "j.clients.kubernetes"

    def get(self, name, ...):
        return KubernetesCluster()


class KubernetesCluster():

    def __init__(self, ...):
        pass

    def ubuntu1604_install(self, sshkey=None):
        """
        deploy base ubuntu container on kubernetes host

        use specified sshkey is name of key !

        if empty use the configured in jumpscale

        @return prefab connection !

        """
        if keyname == None:
            keyname = j.core.state.configMe["ssh"]["sshkeyname"]

    def deploy...():
```
