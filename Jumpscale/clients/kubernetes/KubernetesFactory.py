from Jumpscale import j
from kubernetes import client, config
from .Kubernetes import KubernetesMaster

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class KubernetesFactory(JSConfigBaseFactory):
    """
    kubernetes client factory each instance can relate to either a config file or a context or both
    """
    __jslocation__ = "j.clients.kubernetes"
    _CHILDCLASS = KubernetesMaster

    def create_config(self, config, path=None):
        """
        create config file.

        :param config: the configurations in dict format
        :type config: dict
        :param path: full path to location the file should be saved will default to HOMEDIR/.kube/config
        :type path: str
        """
        if not path:
            directory = '%s/.kube/' % j.dirs.HOMEDIR
            j.sal.fs.createDir(directory)
            path = j.sal.fs.joinPaths(directory, 'config')
        data = j.data.serializers.yaml.dumps(config)
        j.sal.fs.writeFile(path, data)
        self._logger.info('file saved at %s' % path)

    def test(self):
        """
        TODO WIP
        """

        kub = self.get()
        kub.list_clusters()
        kub.list_deployments()
        kub.list_nodes()
        kub.list_pods()
        kub.list_services()
        prefab = kub.deploy_ubuntu1604('tester')
        prefab.core.run('ls')
