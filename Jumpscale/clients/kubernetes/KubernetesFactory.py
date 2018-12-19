from Jumpscale import j
from kubernetes import client, config
from .Kubernetes import KubernetesMaster

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class KubernetesFactory(JSConfigBaseFactory):
    """
    kubernetes client factory each instance can relate to either a config file or a context or both
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.kubernetes"
        JSConfigBaseFactory.__init__(self, KubernetesMaster)

    def create_config(self, config, path=None):
        """
        create config file.

        @param config ,, dict the configurations in dict format
        @param path ,, str full path to location the file should be saved will default to HOMEDIR/.kube/config
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
