#!/usr/bin/env python
from .Container import Container

from Jumpscale import j
import os
import docker
import time
from urllib import parse
import copy
JSBASE = j.application.JSBaseClass


class Docker(j.builder._BaseClass):

    def __init__(self):
        self.__jslocation__ = "j.sal.docker"
        self.__imports__ = "docker"
        JSBASE.__init__(self)
        self._basepath = "/storage/docker"
        self._prefix = ""
        self._containers = None
        self._names = []

        if 'DOCKER_HOST' not in os.environ or os.environ['DOCKER_HOST'] == "":
            self.base_url = 'unix://var/run/docker.sock'
        else:
            self.base_url = os.environ['DOCKER_HOST']
        self.client = docker.APIClient(base_url=self.base_url)

    def _node_set(self, name, sshclient):
        j.tools.nodemgr.set(name, sshclient=sshclient.instance, selected=False,
                            cat="docker", clienttype="j.sal.docker", description="deployment on docker")

    @property
    def containers(self):
        """lists (all) containers
        j.sal.docker.containers
        Returns:
            [Container] -- list of containers
        """

        self._containers = []
        for obj in self.client.containers():
            self._containers.append(Container(obj,self.client))
        return self._containers

    @property
    def docker_host(self):
        """gets docker host name
        j.sal.docker.docker_host
        Returns:
            String -- hostname
        """

        u = parse.urlparse(self.base_url)
        if u.scheme == 'unix':
            return 'localhost'
        else:
            return u.hostname

    @property
    def containers_names_running(self):
        """lists only running containers
        j.sal.docker.containers_names_running
        Returns:
            [Container] -- list of containers
        """

        res = []
        for container in self.containers:
            if container.isRunning():
                res.append(container.name)
        return res
    
    @property
    def containers_names(self):
        """lists only container names
        j.sal.docker.containers_name
        Returns:
            [String] -- list of container names
        """

        res = []
        for container in self.containers:
            res.append(container.name)
        return res

    @property
    def containers_running(self):
        """lists only running containers
        
        Returns:
            [Container] -- list of containers
        """

        res = []
        for container in self.containers:
            if container.is_running():
                res.append(container)
        return res

    def exists(self, name):
        return name in self.containers_names

    @property
    def basepath(self):
        self._basepath = '/mnt/data/docker'
        return self._basepath

    def _getChildren(self, pid, children):
        process = j.sal.process.getProcessObject(pid)
        children.append(process)
        for child in process.get_children():
            children = self._getChildren(child.pid, children)
        return children

    def _get_rootpath(self, name):
        rootpath = j.sal.fs.joinPaths(
            self.basepath, '%s%s' % (self._prefix, name), 'rootfs')
        return rootpath

    def _getMachinePath(self, machinename, append=""):
        if machinename == "":
            raise j.exceptions.RuntimeError("Cannot be empty")
        base = j.sal.fs.joinPaths(self.basepath, '%s%s' %
                                  (self._prefix, machinename))
        if append != "":
            base = j.sal.fs.joinPaths(base, append)
        return base

    def status(self):
        """
        return list docker with some info
        returns [[name, image, sshport, status]]

        """

        res = []
        for item in self.containers:
            res.append([item.name,item.image ,
                        item.ssh_port,item.status])

        return res

    def container_get(self, name, die=True):
        """get a container by name
        j.sal.docker.container_get(name)
        Arguments:
            name {String} -- name of the container
        
        Keyword Arguments:
            die {bool} -- if True it will die if container not found (default: {True})
        
        Raises:
            j.exceptions.RuntimeError -- when no container with this id exists
        
        Returns:
            Container -- container
        """

        for container in self.containers:
            if container.name == name:
                return container
        if die:
            raise j.exceptions.RuntimeError(
                "Container with name %s doesn't exists" % name)
        else:
            return None

    def container_get_by_id(self, id, die=True):
        """get container by id
        j.sal.docker.container_get_by_id(id)
        Arguments:
            id {string} -- id of the container
        
        Keyword Arguments:
            die {bool} -- if True it will die if container not found (default: {True})
        
        Raises:
            j.exceptions.RuntimeError -- when no container with this id exists
        
        Returns:
            Container -- container
        """

        for container in self.containers:
            if container.id == id:
                return container
        if die:
            raise j.exceptions.RuntimeError(
                "Container with name %s doesn't exists" % name)
        else:
            return None

    def _init_aysfs(self, fs, dockname):
        if fs.isUnique():
            if not fs.isRunning():
                self._logger.info('starting unique aysfs: %s' % fs.getName())
                fs.start()

            else:
                self._logger.info(
                    'skipping aysfs: %s (unique running)' % fs.getName())

        else:
            fs.setName('%s-%s' % (dockname, fs.getName()))
            if fs.isRunning():
                fs.stop()

            self._logger.info('starting aysfs: %s' % fs.getName())
            fs.start()

    def create(
            self,
            name="",
            ports="",
            vols="",
            volsro="",
            stdout=True,
            base="phusion/baseimage",
            nameserver=["8.8.8.8"],
            replace=True,
            cpu=None,
            mem=0,
            ssh=True,
            myinit=True,
            sharecode=False,
            sshkeyname="",
            sshpubkey="",
            setrootrndpasswd=True,
            rootpasswd="",
            jumpscalebranch="master",
            aysfs=[],
            detach=False,
            privileged=False,
            getIfExists=True,
            command=""):
        """
        Creates a new container.
        j.sal.docker.create(...)
        @param ports in format as follows  "22:8022 80:8080"  the first arg e.g. 22 is the port in the container
        @param vols in format as follows "/var/insidemachine:/var/inhost # /var/1:/var/1 # ..."   '#' is separator
        @param sshkeyname : use ssh-agent (can even do remote through ssh -A) and then specify key you want to use in docker
        @param ssh : if True it will authorize the sskey name givin and creates a node for it
        """
        if ssh is True and myinit is False:
            raise ValueError("SSH can't be enabled without myinit.")

        name = name.lower().strip()
        self._logger.info(("create:%s" % name))

        running = [item.name for item in self.containers_running]

        if not replace:
            if name in self.containerNamesRunning:
                if getIfExists:
                    return self.container_get(name=name)
                else:
                    j.events.opserror_critical(
                        "Cannot create machine with name %s, because it does already exists.")
        else:
            if self.exists(name):
                self._logger.info("remove existing container %s" % name)
                container = self.container_get(name)
                if container:
                    container.destroy()

        if vols is None:
            vols = ""
        if volsro is None:
            volsro = ""
        if ports is None:
            ports = ""

        if mem is not None:
            if mem > 0:
                mem = int(mem) * 1024
            elif mem <= 0:
                mem = None

        portsdict = {}
        if len(ports) > 0:
            items = ports.split(" ")
            for item in items:
                key, val = item.split(":", 1)
                ss = key.split("/")
                if len(ss) == 2:
                    portsdict[tuple(ss)] = val
                else:
                    portsdict[int(key)] = val

        if ssh:
            if 22 not in portsdict:
                for port in range(9022, 9190):
                    if not j.sal.nettools.tcpPortConnectionTest(self.docker_host, port):
                        portsdict[22] = port
                        self._logger.info(("ssh port will be on:%s" % port))
                        break

        volsdict = {}
        if len(vols) > 0:
            items = vols.split("#")
            for item in items:
                key, val = item.split(":", 1)
                volsdict[str(key).strip()] = str(val).strip()

        if sharecode and j.sal.fs.exists(path="/opt/code"):
            self._logger.info("share jumpscale code enable")
            if "/opt/code" not in volsdict:
                volsdict["/opt/code"] = "/opt/code"

        for fs in aysfs:
            self._init_aysfs(fs, name)
            mounts = fs.getPrefixs()

            for inp, out in mounts.items():
                while not j.sal.fs.exists(inp):
                    time.sleep(0.1)

                volsdict[out] = inp

        volsdictro = {}
        if len(volsro) > 0:
            items = volsro.split("#")
            for item in items:
                key, val = item.split(":", 1)
                volsdictro[str(key).strip()] = str(val).strip()

        self._logger.info("Volumes map:")
        for src1, dest1 in list(volsdict.items()):
            self._logger.info(" %-20s %s" % (src1, dest1))

        binds = {}
        binds2 = []
        volskeys = []  # is location in docker

        for key, path in list(volsdict.items()):
            # j.sal.fs.createDir(path)  # create the path on hostname
            binds[path] = {"bind": key, "ro": False}
            binds2.append("%s:%s" % (path, key))
            volskeys.append(key)

        for key, path in list(volsdictro.items()):
            # j.sal.fs.createDir(path)  # create the path on hostname
            binds[path] = {"bind": key, "ro": True}
            volskeys.append(key)

        if base not in self.images_get():
            self._logger.info("download docker image %s" % base)
            self.pull(base)

        if command == "" and (base.startswith("jumpscale/ubuntu1604") or myinit is True):
            command = "sh -c \" /sbin/my_init -- bash -l\""
        else:
            command = None
        self._logger.info(("install docker with name '%s'" % name))

        if vols != "":
            self._logger.info("Volumes")
            self._logger.info(volskeys)
            self._logger.info(binds)

        hostname = name.replace('_', '-')
        
        for k, v in portsdict.items():
            if isinstance(k, tuple) and len(k) == 2:
                portsdict["%s/%s" % (k[0], k[1])] = v
                portsdict.pop(k)

        host_config = self.client.create_host_config(
            binds=binds2,
            port_bindings=portsdict,
            lxc_conf=None,
            publish_all_ports=False,
            links=None,
            privileged=privileged,
            dns=nameserver,
            dns_search=None,
            volumes_from=None,
            network_mode=None)
        res = self.client.create_container(
            image=base,
            command=command,
            hostname=hostname,
            user="root",
            detach=detach,
            stdin_open=False,
            tty=True,
            ports=list(
                portsdict.keys()),
            environment=None,
            volumes=volskeys,
            network_disabled=False,
            name=name,
            entrypoint=None,
            working_dir=None,
            domainname=None,
            host_config=host_config,
            mac_address=None,
            labels=None,
            stop_signal=None,
            networking_config=None, 
            healthcheck=None, 
            stop_timeout=None, 
            runtime=None)
        if res["Warnings"] is not None:
            raise j.exceptions.RuntimeError(
                "Could not create docker, res:'%s'" % res)

        id = res["Id"]

        res = self.client.start(container=id)

        container = self.container_get_by_id(id)

        if ssh:
            if setrootrndpasswd:
                if rootpasswd is None or rootpasswd == '':
                    rootpasswd = 'gig1234'
            ex = j.tools.executor.getLocalDocker(name)
            ex.execute("apt-get update")
            ex.execute("apt-get install sudo")
            ex.execute("apt-get install openssh-server -y")
            ex.execute("apt-get install sed")
            ex.execute("sed -i 's/prohibit-password/yes/' /etc/ssh/sshd_config")
            ex.execute("service ssh start")
            result = ex.prefab.system.user.passwd("root", rootpasswd)
            container.ssh_authorize(sshkeyname=sshkeyname, password=rootpasswd)

            # Make sure docker is ready for executor
            end_time = time.time() + 60
            while time.time() < end_time:
                rc, _, _ = container.executor.execute('ls /', die=False, showout=False)
                if rc:
                    time.sleep(0.1)
                break

            self._node_set(name, container.sshclient)
        return container

    def images_get(self):
        """lists images
        
        Returns:
            [String] -- list of image names
        """

        images = []
        for item in self.client.images():
            if item['RepoTags'] is None:
                continue
            tags = str(item['RepoTags'][0])
            tags = tags.replace(":latest", "")
            images.append(tags)
        return images

    def images_remove(self, tag="<none>:<none>"):
        """Delete a certain Docker image using tag
        
        Keyword Arguments:
            tag {str} -- images tag (default: {"<none>:<none>"})
        """

        for item in self.client.images():
            if tag in item["RepoTags"]:
                self.client.remove_image(item["Id"])

    def ping(self):
        """pings the docker
        
        Returns:
            bool -- true if ping is successful
        """

        try:
            self.client.ping()
        except Exception as e:
            return False
        return True

    def destroy_all(self, images_remove=False):
        """destroy all containers
        if images_remove is true it will remove all images too
        
        Keyword Arguments:
            images_remove {bool} -- [description] (default: {False})
        """

        for container in self.containers:
            container.destroy()

        if images_remove:
            self.images_remove()

    def _destroyAllKill(self):
        """kills all containers
        """

        if self.ping():

            for container in self.containers:
                container.destroy()

            self.removeImages()

        j.sal.process.execute("systemctl stop docker")

        if j.sal.fs.exists(path="/var/lib/docker/btrfs/subvolumes"):
            j.sal.btrfs.subvolumesDelete('/var/lib/docker/btrfs/subvolumes')

        if j.sal.fs.exists(path="/var/lib/docker/volumes"):
            for item in j.sal.fs.listDirsInDir("/var/lib/docker/volumes"):
                j.sal.fs.remove(item)

    def removeDocker(self):
        self._destroyAllKill()

        rc, out, _ = j.sal.process.execute("mount")
        mountpoints = []
        for line in out.split("\n"):
            if line.find("type btrfs") != -1:
                mountpoint = line.split("on ")[1].split("type")[0].strip()
                mountpoints.append(mountpoint)

        for mountpoint in mountpoints:
            j.sal.btrfs.subvolumesDelete(mountpoint, "/docker/")

        j.sal.btrfs.subvolumesDelete("/storage", "docker")

        j.sal.process.execute("apt-get remove docker-engine -y")
        # j.sal.process.execute("rm -rf /var/lib/docker")

        j.sal.fs.remove("/var/lib/docker")

    def reInstallDocker(self):
        """
        ReInstall docker on your system
        """
        self.removeDocker()

        j.tools.prefab.local.docker.install(force=True)

        self.init()

    def pull(self, imagename):
        """
        pull a certain image.
        @param imagename string: image
        """
        self.client.import_image_from_image(imagename)

    def push(self, image, output=True):
        """
        image: str, name of the image
        output: print progress as it pushes
        """
        client = self.client
        previous_timeout = client.timeout
        client.timeout = 36000
        out = []
        for l in client.push(image, stream=True):
            line = j.data.serializers.json.loads(l)
            id = line['id'] if 'id' in line else ''
            s = "%s " % id
            if 'status' in line:
                s += line['status']
            if 'progress' in line:
                detail = line['progressDetail']
                progress = line['progress']
                s += " %50s " % progress
            if 'error' in line:
                message = line['errorDetail']['message']
                raise j.exceptions.RuntimeError(message)
            if output:
                self._logger.info(s)
            out.append(s)

        client.timeout = previous_timeout

        return "\n".join(out)

    def build(self, path, tag, output=True, force=False):
        """
        path: path of the directory that contains the docker file
        tag: tag to give to the image. e.g: 'jumpscale/myimage'
        output: print output as it builds

        return: string containing the stdout
        """
        out = []
        if force:
            nocache = True
        for l in self.client.build(path=path, tag=tag, nocache=nocache):
            line = j.data.serializers.json.loads(l)
            if 'stream' in line:
                line = line['stream'].strip()
                if output:
                    self._logger.info(line)
                out.append(line)

        return "\n".join(out)
