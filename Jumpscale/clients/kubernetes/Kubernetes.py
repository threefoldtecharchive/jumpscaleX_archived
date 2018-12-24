from kubernetes import client, config
import time
import urllib
from Jumpscale import j

TEMPLATE = """
config_path = ""
context = ""
sshkey_path = ""
incluster_config = false
"""


JSConfigBase = j.application.JSBaseClass
JSBASE = j.application.JSBaseClass


class KubernetesMaster(JSConfigBase):
    """
    A class that represents a top view of the hirarchy.
    Where only the config, context , or namespace are defined.
    """

    def __init__(self, instance, data={}, parent=None, interactive=False):
        """
        Creates a client instance that connects to either a config path or context or both
        """
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        # load data from jsconfig
        c = self.config.data
        config_path = c['config_path']
        context = c['context']
        sshkey_path = c['sshkey_path']
        incluster_config = c['incluster_config']

        if incluster_config:
            config.load_incluster_config()
        else:
            config.load_kube_config(config_file=config_path, context=context)
        self._v1 = client.CoreV1Api()
        self._extensionv1b1 = client.ExtensionsV1beta1Api(
            api_client=self._v1.api_client)
        if not config_path:
            config_path = '%s/.kube/config' % j.dirs.HOMEDIR
        self._config = j.data.serializers.yaml.load(config_path)

        self.sshkey_path = sshkey_path
        if not sshkey_path:
            self.sshkey_path = j.sal.fs.joinPaths(
                j.dirs.HOMEDIR, '.ssh', j.core.state.configMe["ssh"]["sshkeyname"])

    @property
    def namespaces(self):
        """
        get a list of all available namespaces and their relevant information.
        """
        output = list()
        namespace_list = self._v1.list_namespace()
        for namespace in namespace_list.items:
            namespace_dict = {'name': namespace.metadata.name,
                              'cluster_name': namespace.metadata.cluster_name,
                              'status': namespace.status.phase}
            output.append(namespace_dict)
        return output

    def get_namespace(self, name):
        """
        Get namespace object with specified name.
        @param name,, str name of namespace.
        """
        return self._v1.read_namespace(name)

    @property
    def clusters(self):
        """
        get a list of all available clusters and their relevant information.
        """
        return self._config.get('clusters', [])

    def get_cluster(self, name):
        """
        will get the cluster with the defined name.

        @param name,, str name of cluster to get
        """
        for cluster in self._config.get('clusters', []):
            if name == cluster['name']:
                return cluster


#######################
#      master.NODE    #
#######################

    def get_node(self, name):
        """
        will get the cluster with the defined name.
        @param name ,, str node name.
        """
        return self._v1.read_node(name=name)

    def list_nodes(self, label='', short=True):
        """
        will get all nodes within the defined label.
        @param label,, dict labels to filter on. example {'beta.kubernetes.io/arch': 'amd64',
                                                         'beta.kubernetes.io/os': 'linux',
                                                         'kubernetes.io/hostname': 'minikube'}
        @param short,, bool return small dict if true return full object if false
        """
        nodes = self._v1.list_node(label_selector=label).items
        if short:
            output = []
            for node in nodes:
                node_dict = {'name': node.metadata.name,
                             'image': node.status.node_info.os_image,
                             'addresses': node.status.addresses}
                output.append(node_dict)
            return output
        return nodes


######################
#  master.DEPLOYMENT #
######################

    def get_deployment(self, name, namespace='default'):
        """
        will get the deployment with the defined name and namespace.
        if no namespace defined , will default to the 'default' name space : !! important.
        @param name ,, str deployment name.
        @param namespace,, str namespace to filter on.
        """
        dep_obj = self._extensionv1b1.read_namespaced_deployment(name, namespace)
        return Deployment(dep_obj.metadata.name, self, [], deployment_object=dep_obj)

    def list_deployments(self, namespace=None, short=True):
        """
        will get all deployment within the defined namespace(if no space given will return all).
        @param namespace,, str namespace to filter on.
        @param short,, bool return small dict if true return full object if false
        """
        deployments = []
        if namespace:
            deployment_objects = self._extensionv1b1.list_namespaced_deployment(
                namespace).items
        else:
            deployment_objects = self._extensionv1b1.list_deployment_for_all_namespaces().items
        if short:
            output = []
            for dep in deployment_objects:
                dep_dict = {'name': dep.metadata.name,
                            'namespace': dep.metadata.namespace,
                            'replicas': dep.status.replicas}
                output.append(dep_dict)
            return output
        for dep_obj in deployment_objects:
            deployments.append(Deployment(dep_obj.metadata.name, self, [], deployment_object=deployment_object))
        return deployments

    def define_deployment(self, name, containers, namespace='default', labels={}, replicas=1, kind='Deployment',
                          cluster_name=None, generate_name=None, volumes=[]):
        """
        define a new deployment returning the Deployment object.

        @param name,, str name of deployment
        @param containers,, list(V1Container) can be defined through the self.define_container method
        @param namespace,, namespace to tag the deployment with
        @param labels,, dict can be used to specify selectors for filtering and group actions
        @param replicas,,int number of replicas that will be maintained running throughout the life of the deployment
        @param kind,, str kind of object to be defined , will default to Deployment
        @param cluster_name,, str cluster or context to create deployment on
        @param generate_name,,str first part of the generated name
        """
        api_version = 'extensions/v1beta1'
        return Deployment(name, master=self, namespace=namespace, containers=containers, labels=labels,
                          replicas=replicas, api_version=api_version, cluster_name=cluster_name,
                          generate_name=generate_name, volumes=volumes)

    def deploy_ubuntu1604(self, name, namespace='default', labels={}, replicas=1, generate_name=None,
                          sshkey_path=None, external_ssh_port=32202, volumes=[], volume_mounts=[]):
        """
        Creates and deploys a ubuntu1604 phusion image  deployment that has a ssh configured.
        @param name,, str name of deployment
        @param namespace,, namespace to tag the deployment with
        @param labels,, dict can be used to specify selectors for filtering and group actions
        @param replicas,,int number of replicas that will be maintained running throughout the life of the deployment.
        @param cluster_name,, str cluster or context to create deployment on. NOT SUPPORTED by the api server
        @param generate_name,,str first part of the generated name
        @param sshkey_path,,str path to new ssh key if none will default to preloaded key
        @param external_ssh_port,,int external port to map the ssh 22 port to.
        """
        # define container
        container = self.define_container(name='ubuntu1604', image='jumpscale/ubuntu1604', command=['/sbin/my_init'],
                                          ports=[22], enable_ssh=True, sshkey_path=sshkey_path,
                                          volume_mounts=volume_mounts)
        app_label = {'app': name}
        labels.update(app_label)
        deployment = self.define_deployment(name=name, labels=labels, namespace=namespace, containers=[container],
                                            replicas=replicas, generate_name=generate_name, volumes=volumes)
        deployment.create()
        ssh_service = self.define_ssh_service(
            name, app_label['app'], external_ssh_port)
        ssh_service.create()
        clusters = self._config.get('clusters')
        if not clusters:
            raise RuntimeError('no Clusters defined this your configuration is incorrect')

        api_server_endpoint = urllib.parse.urlsplit(clusters[0]['cluster']['server'])
        node_ip = api_server_endpoint.hostname
        return j.tools.prefab.get('%s:%s' % (node_ip, external_ssh_port))

######################
#  master.VOLUMES    #
######################

    def define_host_path_volume(self, name, path, data_type=''):
        """
        Represents a host path on the node mapped into a pod. This does not change permissions and kubernetes is not
        responsible for creating the path location or managing it , it only uses the volume for mounting and checking
        on the type of the path Host path volumes do not support ownership management or SELinux relabeling.

        @param name ,, str name of volume that is created.
        @param path ,, str path of the directory on the host. If the path is a symlink, it will follow the link to the real path.
        @param type ,, str Type for HostPath Volume Defaults to "".
        """
        host_path_vol = client.V1HostPathVolumeSource(path=path, type=data_type)
        return client.V1Volume(name=name, host_path=host_path_vol)

    def define_config_map_volume(self, name, config_name, config_items, default_mode=0o644, optional=False):
        """
        The contents of the target ConfigMap's Data field will be presented in a volume as files using the keys in the
        Data field as the file names, unless the items element is populated with specific mappings of keys to paths.
        ConfigMap volumes support ownership management and SELinux relabeling.

        @param name ,, str name of volume that is created.
        @param config_name ,, str name of the config map being used
        @param config_items ,,dict key value to project and The relative path of the file to map the key to. May not be an absolute path. May not contain the path element '..'. May not start with the string '..'.
        @param default_mode ,, int mode bits to use on created files by default. Must be a value between 0 and 0777. Defaults to 0644. Directories within the path are not affected by this setting. This might be in conflict with other options that affect the file mode, like fsGroup, and the result can be other mode bits set.
        @param optional ,,bool Specify whether the ConfigMap or it's keys must be defined
        """
        config_map_vol = client.V1ConfigMapVolumeSource(default_mode=default_mode, optional=optional, name=config_name,
                                                        items=config_items)
        return client.V1Volume(name=name, config_map=config_map)

    def define_empty_dir_volume(self, name, medium="", size_limit=None):
        """
        Represents an empty directory for a pod. Empty directory volumes support ownership management and SELinux
        relabeling by default, emptyDir volumes are stored on whatever medium is backing the node - that might be disk
        or SSD or network storage, depending on your environment. However, you can set the emptyDir.medium field to
        "Memory" to tell Kubernetes to mount a tmpfs (RAM-backed filesystem) for you instead. While tmpfs is very fast,
        be aware that unlike disks, tmpfs is cleared on node reboot and any files you write will count against your
        container’s memory limit.

        @param name ,, str name of volume that is created.
        @param medium ,,str What type of storage medium should back this directory. The default is "" which means to use the node's default medium. Must be an empty string (default) or Memory.
        @param size_limit ,,int Total amount of local storage required for this EmptyDir volume.
        """
        empty_dir_vol = client.V1EmptyDirVolumeSource(medium=medium, size_limit=sizeLimit)
        return client.V1Volume(name=name, empty_dir=empty_dir_vol)

    def define_git_volume(self, name, directory, repo, revision=None):
        """
        Represents a volume that is populated with the contents of a git repository. Git repo volumes do not support
        ownership management. Git repo volumes support SELinux relabelin.

        @param name ,, str name of volume that is created.
        @param directory ,, str Target directory name. Must not contain or start with '..'. If '.' is supplied, the volume directory will be the git repository. Otherwise, if specified, the volume will contain the git repository in the subdirectory with the given name.
        @param repo ,, str  Repository URL
        @param revision ,, str  Commit hash for the specified revision.
        """
        git_vol = client.V1GitRepoVolumeSource(directory=directory, repository=repo, revision=revision)
        return client.V1Volume(name=name, git_repo=git_vol)

    def define_persistent_volume_claim(self):
        """
        define persistent volume claim
        TODO
        """

######################
#     master.POD     #
######################

    def get_pod(self, name, namespace='default'):
        """
        will get the pod with the defined name and namespace.
        if no namespace defined , will default to the 'default' name space : !! important.
        @param name ,, str deployment name.
        @param namespace,, str namespace to filter on.
        """
        pod_obj = self._v1.read_namespaced_pod(name, namespace)
        return Pod(pod_obj.metadata.name, self, [], pod_object=pod_object)

    def list_pods(self, namespace=None, short=True):
        """
        will get all pod within the defined namespace(if no space given will return all).
        @param namespace,, str namespace to filter on.
        @param short,, bool return small dict if true return full object if false
        """
        if namespace:
            pod_objects = self._v1.list_namespaced_pod(namespace).items
        else:
            pod_objects = self._v1.list_pod_for_all_namespaces().items
        if short:
            output = []
            for pod in pod_objects:
                pod_dict = {'name': pod.metadata.name,
                            'namespace': pod.metadata.namespace,
                            'status': pod.status.phase,
                            'ip': pod.status.pod_ip}
                output.append(pod_dict)
            return output
        return [Pod(pod_object.metadata.name, self, [], pod_object=pod_object)for pod_object in pod_objects]

    def define_pod(self):
        """
        define a Pod object instance
        TODO
        """
        # return Pod(name, master, containers, labels, replicas, api_version, kind, ssh_key)

    def define_affinity(self):
        """
        define affinity object to be passed to a pod, deployment or statefulset
        TODO
        """

######################
#   master.Container #
######################

    def define_container(self, name, image, ports=[], command=None, args=None, sshkey_path=None, enable_ssh=False,
                         envs=[], volume_mounts=[]):
        """
        define container object to be passed to pod creation or deployment

        @param name,,str name of the container
        @param image,,str name (full path) of image
        @param ports,,list(int) list of ports to expose to the node
        @param command,, list(str) entry point to the docker
        @param args ,, list(str) args to be passed to the entry point
        @param sshkey_path,, str full path to ssh_key will work only if enable_ssh is true
        @param enable_ssh,, bool if True and no key is passed will load the default loaded one in jumpscale me configs
        @param envs,, list({'key':'value'}) environment variable to define in the container
        @param volume_mounts,, list(volume_mounts) volumes to mount to the containers created from define mount
        """
        envs = [client.V1EnvVar(env.key, env.value) for env in envs]

        # get ssh_pub_key if not provided will default to the preloaded
        if enable_ssh:
            if sshkey_path:
                pub_key = j.sal.fs.readFile(sshkey_path)
            else:
                pub_key = j.sal.fs.readFile(self.sshkey_path)
            # the key must be added in the command to be executed on restarts and recovery.
            joined_command = ''
            joined_args = ''
            new_command_args = ''
            if command:
                joined_command = "".join(command)
                if args:
                    joined_args = "".join(args)
                new_command_args = "&& %s %s" % (joined_command, joined_args)
            envs.append(client.V1EnvVar('PUBSSHKEY', pub_key))
            command = ['/bin/bash']
            args = [
                "-c", "service ssh start && mkdir -p /root/.ssh/ && echo ${PUBSSHKEY} > /root/.ssh/authorized_keys %s" % new_command_args]

        # Configureate Pod template container
        container_ports = [client.V1ContainerPort(
            container_port=port) for port in ports]
        container = client.V1Container(
            name=name, image=image, env=envs, ports=container_ports, command=command, args=args, stdin=True, volume_mounts=volume_mounts)
        return container
# The client can be extended for container , but at the moment does not seem necessary.

    def define_mount(self, name, mount_path, read_only=False, sub_path=""):
        """
        define the mount on the container to attach a volume.

        @param name,, This must match the Name of a Volume.
        @param mountPath,, Path within the container at which the volume should be mounted. Must not contain ':'.
        @param readOnly,, Mounted read-only if true, read-write otherwise (false or unspecified). Defaults to false.
        @param subPath,,Path within the volume from which the container's volume should be mounted. Defaults to "" (volume's root).
        """
        return client.V1VolumeMount(name=name, mount_path=mount_path, read_only=read_only, sub_path=sub_path)

######################
#    master.Service  #
######################

    def get_service(self, name, namespace='default'):
        """
        will get the service with the defined name and namespace.
        if no namespace defined , will default to the 'default' name space : !! important.
        @param name ,, str deployment name.
        @param namespace,, str namespace to filter on.
        """
        service_object = self._v1.read_namespaced_service(name, namespace)
        return Service(service_object.metadata.name, self, service_object=service_object)

    def list_services(self, namespace=None, short=True):
        """
        will get all services within the defined namespace(if no space given will return all).
        @param namespace,, str namespace to filter on.
        @param short,, bool return small dict if true return full object if false
        """
        services = []
        if namespace:
            service_objs = self._v1.list_namespaced_service(namespace).items
        else:
            service_objs = self._v1.list_service_for_all_namespaces().items
        if short:
            output = []
            for service in service_objs:
                service_dict = {'name': service.metadata.name,
                                'namespace': service.metadata.namespace,
                                'ports': service.spec.ports}
                output.append(service_dict)
            return output
        for service_obj in service_objs:
            services.append(Service(service_obj.metadata.name, self, service_object=service_obj))
        return services

    def define_service(self, name, selector, ports, protocol=None, service_type='LoadBalancer'):
        """
        define service object returning the Service object.
        @param name ,, name of the service that will be created , prefered to be the same as the selector app value.
        @param ports ,, list(str) list of comma seprated string [internalport:externalport], e.g. ['22:2202']
        @param selector ,,list({string:string})  points towards the app the service will expose usually {'app':appname}
        @param protocol ,, str tcp or udp , default to tcp
        @param service_type,, determine the typed of networking service to create , can be ClusterIP , NodePort, or LoadBalancer
        """
        return Service(name=name, master=self, selector=selector, ports=ports, protocol=protocol,
                       service_type=service_type)

    def define_ssh_service(self, name, app, external_port):
        """
        creates and deploys the Service that does the portforwarding for ssh from the pod to outside the node.
        ssh service, keys, and  port need to be configured withing the pod or deployment.
        @param name,, str name of the service
        @param app,, str app label that relates to the deployment or deployments to allow ssh on
        @param external_port,, int external port to map the ssh 22 port to.
        """
        port = ['22:%d' % external_port]
        service = self.define_service(name, {'app': app}, port, service_type='NodePort')
        return service


######################
#     DEPLOYMENT     #
######################

class Deployment(j.application.JSBaseClass):
    """
    Kubernetes cluster wrapper layer.
    """

    def __init__(self, name, master, containers, labels={}, replicas=1, api_version='extensions/v1beta1',
                 cluster_name=None, namespace='default', generate_name=None, min_ready_seconds=0,
                 progress_deadline_seconds=600, deployment_strategy_type='RollingUpdate',
                 dns_policy='ClusterFirstWithHostNet', deployment_strategy_rolling_update=None, selectors=None,
                 deployment_object=None, volumes=[]):
        """
        Create a new deployment object in the specified cluster with specified label.

        @param name,,str name of the deployment.
        @param master,, KubernetesMaster the master object that has all the clients and the config to connect to.
        @param containers,, list(V1Container) this can be produces using the self.define_container method on mater.
        @param labels,,list({string:string}) labels to apply to the pod
        @param replicas,, number of replicas to maintain until the end of lifetime of deployment.
        @param cluster_name,,str cluster to create the pod on
        @param namespace,, str namespace to relate the pod to
        @param dns_policy,,str set DNS policy for containers within the pod. One of 'ClusterFirstWithHostNet', 'ClusterFirst' or 'Default'. Defaults to "ClusterFirst". To have DNS options set along with hostNetwork, you have to specify DNS policy explicitly to 'ClusterFirstWithHostNet'.
        @param selector,,{string:string}  is a selector which must be true for the deployment to fit on a node or cluster.
        @param generate_name,, str the generated name for deployment.
        @param progress_deadline_seconds,, int The maximum time in seconds for a deployment to make progress before it is considered to be failed. The deployment controller will continue to process failed deployments and a condition with a ProgressDeadlineExceeded reason will be surfaced in the deployment status. Note that progress will not be estimated during the time a deployment is paused. Defaults to 600s.
        @param deployment_strategy_type,, str Type of deployment. Can be "Recreate" or "RollingUpdate". Default is RollingUpdate.
        @param deployment_strategy_rolling_update,, {maxSurge:int, maxUnavailable: int}
        @param min_ready_seconds,, int Minimum number of seconds for which a newly created pod should be ready without any of its container crashing, for it to be considered available. Defaults to 0 (pod will be considered available as soon as it is ready)
        @param volumes,, list(V1Volume) can be created from the define_?_volume methods
        """
        JSBASE.__init__(self)
        self.object = deployment_object
        if not deployment_object:
            kind = 'Deployment'
            labels.update({'app': name})
            # Create and configure pod spec section
            pod_spec = client.V1PodTemplateSpec(metadata=client.V1ObjectMeta(labels=labels),
                                                spec=client.V1PodSpec(containers=containers, dns_policy=dns_policy,
                                                                      volumes=volumes))

            # create deployment_strategy
            deployment_strategy = client.AppsV1beta1DeploymentStrategy(rolling_update=deployment_strategy_rolling_update,
                                                                       type=deployment_strategy_type)

            # Create the specification of deployment
            selector = None
            if selectors:
                selector = client.V1LabelSelector([], selectors)

            deployment_spec = client.ExtensionsV1beta1DeploymentSpec(replicas=replicas, template=pod_spec,
                                                                     progress_deadline_seconds=progress_deadline_seconds,
                                                                     min_ready_seconds=min_ready_seconds,
                                                                     strategy=deployment_strategy, selector=selector)
            # Instantiate the deployment object
            self.object = client.ExtensionsV1beta1Deployment(api_version=api_version, kind=kind, spec=deployment_spec,
                                                             metadata=client.V1ObjectMeta(name=name, cluster_name=cluster_name, namespace=namespace,
                                                                                          generate_name=generate_name))
        self.master = master

    def __str__(self):
        return self.object.to_str()

    def __dict__(self):
        return self.object.to_dict()

    def __repr__(self):
        return self.object.__repr__()

    def create(self):
        """
        Create a new deployment.
        @param deployment ExtensionsV1beta1Deployment (an object that is created through self.define_deployment)
        """
        # Create deployment
        api_response = self.master._extensionv1b1.create_namespaced_deployment(
            body=self.object, namespace=self.object.metadata.namespace)
        self._logger.info("Deployment created. status='%s'" % str(api_response.status))

    def update(self):
        """
        Update the  deployment by applying the changes the happened in the deployment object.
        @param deployment,, ExtensionsV1beta1Deployment (an object that is created through self.define_deployment)
        """
        # Update the deployment
        api_response = self.master._extensionv1b1.patch_namespaced_deployment(name=self.object.metadata.name,
                                                                              namespace=self.object.metadata.namespace,
                                                                              body=self.object)
        self._logger.info("Deployment updated. status='%s'" % str(api_response.status))

    def delete(self, grace_period_seconds=0, propagation_policy='Foreground'):
        """
        delete the named deployment.
        @param name,, str :name of the deployment.
        @param grace_period_seconds,, int :The duration in seconds before the object should be deleted.
        @param propagation_policy,, str :Whether and how garbage collection will be performed.
        """
        # delete options
        delete_options = client.V1DeleteOptions(propagation_policy=propagation_policy,
                                                grace_period_seconds=grace_period_seconds)
        # Delete deployment
        api_response = self.master._extensionv1b1.delete_namespaced_deployment(name=self.object.metadata.name,
                                                                               namespace=self.object.metadata.namespace,
                                                                               body=delete_options)
        self._logger.info("Deployment deleted. status='%s'" % str(api_response.status))

######################
#     POD            #
######################


class Pod(client.V1Pod, JSBASE):
    """
    Kubernetes Pod wrapper layer.
    """

    def __init__(self, name, master, containers, namespace='default', cluster_name=None, host_aliases={},
                 dns_policy='ClusterFirstWithHostNet', labels={}, host_network=True, hostname=None,
                 init_containers=None, node_name=None, node_selector=None, subdomain=None, volumes=None,
                 pod_object=None):
        """
        Create a new pod object in the specified cluster with specified label.

        @param name,,str name of the deployment
        @param master,, KubernetesMaster the master object that has all the clients and the config to connect to.
        @param containers,, list(V1Container) this can be produces using the self.define_container method on mater.
        @param namespace,, str namespace to relate the pod to
        @param cluster_name,,str cluster to create the pod on
        @param host_aliases,,list({hostname: ip}) is an optional list of hosts and IPs that will be injected into the pod's hosts file if specified. This is only valid for non-hostNetwork pods.
        @param dns_policy,,str set DNS policy for containers within the pod. One of 'ClusterFirstWithHostNet', 'ClusterFirst' or 'Default'. Defaults to "ClusterFirst". To have DNS options set along with hostNetwork, you have to specify DNS policy explicitly to 'ClusterFirstWithHostNet'.
        @param labels,,list({string:string}) labels to apply to the pod
        @param host_network,,bool Host networking requested for this pod. Use the host's network namespace. If this option is set, the ports that will be used must be specified. Default to false.
        @param hostname,,str Specifies the hostname of the Pod If not specified, the pod's hostname will be set to a system-defined value.
        @param init_containers,, list(V1Container) List of initialization containers belonging to the pod. Init containers are executed in order prior to containers being started. If any init container fails, the pod is considered to have failed and is handled according to its restartPolicy. The name for an init container or normal container must be unique among all containers. Init containers may not have Lifecycle actions, Readiness probes, or Liveness probes. The resourceRequirements of an init container are taken into account during scheduling by finding the highest request/limit for each resource type, and then using the max of of that value or the sum of the normal containers. Limits are applied to init containers in a similar fashion. Init containers cannot currently be added or removed. Cannot be updated. More info: https://kubernetes.io/docs/concepts/workloads/pods/ini
        @param node_name,,str NodeName is a request to schedule this pod onto a specific node. If it is non-empty, the scheduler simply schedules this pod onto that node, assuming that it fits resource requirements.
        @param node_selector,,list({string:string}) NodeSelector is a selector which must be true for the pod to fit on a node. Selector which must match a node's labels for the pod to be scheduled on that node. More info: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/
        @param subdomain,,str If specified, the fully qualified Pod hostname will be "...svc.". If not specified, the pod will not have a domainname at all.
        """
        JSBASE.__init__(self)
        self.object = pod_object
        if not pod_object:
            # create metadata for the pod
            metadata = client.V1ObjectMeta(
                name=name, cluster_name=cluster_name, namespace=namespace, labels=labels)

            # get volumes
            volume_objects = []
            for volume in volumes:
                volume_objects.append(master._v1.read_persistent_volume(volume))

            # Create and configure pod spec section
            pod_spec = client.V1PodSpec(host_aliases=host_aliases, dns_policy=dns_policy, containers=containers,
                                        host_network=host_network, hostname=hostname, init_containers=init_containers,
                                        node_name=node_name, node_selector=node_selector, restart_policy='Always',
                                        subdomain=subdomain, volumes=volumes)

            self.object = client.V1Pod('v1', 'Pod', metadata=metadata, spec=pod_spec)

        self.master = master

    def __str__(self):
        return self.object.to_str()

    def __dict__(self):
        return self.object.to_dict()

    def __repr__(self):
        return self.object.__repr__()

    def create(self):
        """
        Create a new pod.
        """
        # Create deployment
        api_response = self.master._extensionv1b1.create_namespaced_pod(
            body=self.object, namespace=self.object.metadata.namespace)
        self._logger.info("Pod created. status='%s'" % str(api_response.status))

    def update(self):
        """
        Update the  pod by applying the changes the happened in the pod object.
        """
        # Update the pod
        api_response = self.master._extensionv1b1.patch_namespaced_pod(name=self.object.metadata.name,
                                                                       namespace=self.object.metadata.namespace,
                                                                       body=self.object)
        self._logger.info("Pod updated. status='%s'" % str(api_response.status))

    def delete(self, grace_period_seconds=0, propagation_policy='Foreground'):
        """
        delete the pod the object relates to.
        @param name,, str :name of the pod.
        @param grace_period_seconds,, int :The duration in seconds before the object should be deleted.
        @param propagation_policy,, str :Whether and how garbage collection will be performed.
        """
        # delete options
        delete_options = client.V1DeleteOptions(propagation_policy=propagation_policy,
                                                grace_period_seconds=grace_period_seconds)
        # Delete pod
        api_response = self.master._extensionv1b1.delete_namespaced_pod(name=self.object.metadata.name,
                                                                        namespace=self.object.metadata.namespace,
                                                                        body=delete_options)
        self._logger.info("Pod deleted. status='%s'" % str(api_response.status))


######################
#     Service        #
######################


class Service(client.V1Service, JSBASE):

    def __init__(self, name, master, selector=None, ports=None, namespace='default', protocol='tcp', service_type='LoadBalancer',
                 service_object=None):
        """
        Create a new Service object in the specified cluster with specified selector and other options.

        @param name,, name of the service object
        @param master,, KubernetesMaster the master object that has all the clients and the config to connect to.
        @param selector,,list({string:string})  points towards the app the service will expose usually {'app':appname}
        @param namespace,, str namespace to relate the service to
        @param ports ,, list(str) list of comma seprated string [internalport:externalport], e.g. ['22:32202']
        @param protocol,,str tcp or udp , default to tcp
        @param service_type,,str type determines how the Service is exposed. Defaults to ClusterIP. Valid options are ExternalName, ClusterIP, NodePort, and LoadBalancer. "ExternalName" maps to the specified externalName. "ClusterIP" allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are determined by the selector or if that is not specified, by manual construction of an Endpoints object. If clusterIP is "None", no virtual IP is allocated and the endpoints are published as a set of endpoints rather than a stable IP. "NodePort" builds on ClusterIP and allocates a port on every node which routes to the clusterIP. "LoadBalancer" builds on NodePort and creates an external load-balancer (if supported in the current cloud) which routes to the clusterIP. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services---service-types
        """
        JSBASE.__init__(self)
        self.object = service_object
        if not service_object:
            # create etadata for the service
            metadata = client.V1ObjectMeta(name=name, namespace=namespace)
            service_ports = []
            for port_pair in ports:
                if service_type == 'LoadBalancer' or service_type == 'ClusterIP':
                    internal_port, _ = port_pair.split(':')
                    service_ports.append(client.V1ServicePort('%s-%s' % (name, internal_port),
                                                              port=int(internal_port), protocol=protocol))
                else:
                    internal_port, external_port = port_pair.split(':')
                    service_ports.append(client.V1ServicePort('%s-%s-%s' % (name, internal_port, external_port),
                                                              port=int(internal_port), node_port=int(external_port),
                                                              protocol=protocol))

            # create the specs
            service_spec = client.V1ServiceSpec(
                selector=selector, ports=service_ports, type=service_type)

            # define the service
            self.object = client.V1Service(api_version='v1', kind='Service',
                                           metadata=metadata, spec=service_spec)
        self.master = master

    def __str__(self):
        return self.object.to_str()

    def __dict__(self):
        return self.object.to_dict()

    def __repr__(self):
        return self.object.__repr__()

    def create(self):
        """
        Create a new service.
        """
        # Create deployment
        api_response = self.master._v1.create_namespaced_service(
            body=self.object, namespace=self.object.metadata.namespace)
        self._logger.info("service created. status='%s'" % str(api_response.status))

    def update(self):
        """
        Update the  service by applying the changes the happened in the service object.
        """
        # Update the service
        api_response = self.master._v1.patch_namespaced_service(name=self.object.metadata.name,
                                                                namespace=self.object.metadata.namespace,
                                                                body=self.object)
        self._logger.info("service updated. status='%s'" % str(api_response.status))

    def delete(self):
        """
        delete the named service.
        @param name,, str :name of the service.
        """
        # Delete service
        api_response = self.master._v1.delete_namespaced_service(name=self.object.metadata.name,
                                                                 namespace=self.object.metadata.namespace)
        self._logger.info("service deleted. status='%s'" % str(api_response.status))
