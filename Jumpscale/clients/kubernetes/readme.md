# Kubernetes client for jumpscale
Jumpscale provides a wrapper client around the api server of kubernetes which basicly provides control over all the clusters within the specified config.

## __Setting up the cluster__

The client is designed to provide objects and classes that follow the DSL format that jumpscale conforms to.
To start using the client , a cluster must be setup there mulltiple ways to do that which include but are not limited to :
 - [minikube](https://github.com/kubernetes/minikube)
 - [google containers platform](https://cloud.google.com/container-engine/docs/quickstart)

Other methods can be found at https://kubernetes.io/docs/setup/pick-right-solution/.


## __Using the client__

The cluster or context that the client will connect to will rely completly on the configuration, which is going to be a
yaml file.
The file can also be created through a create_config method located on the kubernetes entry point:
```python
example_config_dict = {
    "apiVersion": "v1",
    "clusters": [
        {
            "cluster": {
                "certificate-authority": "/home/art/.minikube/ca.crt",
                "server": "https://192.168.99.100:8443"
            },
            "name": "minikube"
        }
    ],
    "contexts": [
        {
            "context": {
                "cluster": "minikube",
                "user": "minikube"
            },
            "name": "minikube"
        }
    ],
    "current-context": "minikube",
    "kind": "Config",
    "preferences": {},
    "users": [
        {
            "name": "cluster-admin",
            "user": {
                "as-user-extra": {},
                "password": "admin",
                "username": "admin"
            }
        },
        {
            "name": "minikube",
            "user": {
                "as-user-extra": {},
                "client-certificate": "/home/art/.minikube/client.crt",
                "client-key": "/home/art/.minikube/client.key"
            }
        }
    ]
}
j.clients.kubernetes.create_config(example_config_dict)
```
Then to get the client Object the config_path is passed if no path is passed will default to HOMEDIR/.kube/config :
```python
kub_client = j.clients.kubernetes.get(config_path)
```
Now that you have the client you can list domains, pods, services, for easier view a short parameter can be passed to
return only a small list of dicts instead of the objects for easier readability and access:

```python
kub_client.list_deployments(short=True)
```
There are many ways to deploy the easiest is the define deployment, service, pod methods which both creates the object
and deploys it.

It is important to know that before creating a pod or a deployment a container must be defined this
is done to allow more flexibility when defining the number of containers withing a pod or deployment
for example:
```python
container = kub_client.define_container('test_container', 'nginx', [80])
deployment = kub_client.define_deployment(name, [container],  replicas=2)
```
Kubernetes also supports volumes , this is avaliable through the client, by specifiying a volume and a volume mount with the same name , this is done to allow for seperation between the actual mount and the volume. This means that volumes can be used multiple times within a deployment and if the same volume object is passed to other deployments it can be used there as well.
Creating the mount and volume is very simple for example:
```python
volume = kub_client.define_git_volume('filewalker', '', 'https://github.com/abdulrahmantkhalifa/fillewalker.git')
mount =  kub_client.define_mount('filewalker', '/opt')
container = kub_client.define_container('test_container', 'nginx', [80], volume_mount=mount)
deployment = kub_client.define_deployment(name, [container],  replicas=2, volumes=[volume])
```

## __Create Deployment with ubuntu1604 image__

For more abstracted view, you can directly deploy an ubuntu1604 image with ssh enabled and your key added directly using
one command to do that:
```python
sshkey_path = '%s/.ssh/id_rsa.pub' % j.dirs.HOMEDIR
prefab_client = kub_client.deploy_ubuntu1604('tester', sshkey_path=sshkey_path)
```
This method creates the deployment and in turn pods and container, it also creates a load balancing service to expose
the container ip to a public ip.

(!! IMPORTANT some services can incur additional charges on some cloud providers)

The method returns a prefab client connected to the container allowing all the functionality of the prefab tool within
that container



