import shlex
import json
from .BaseClient import BaseClient
from .Response import JSONResponse
from .FlistManager import FlistManager

from . import typchk

DefaultTimeout = 10  # seconds


class ContainerClient(BaseClient):
    class ContainerZerotierManager:
        def __init__(self, client, container):
            self._container = container
            self._client = client

        def info(self):
            return self._client.json("corex.zerotier.info", {"container": self._container})

        def list(self):
            return self._client.json("corex.zerotier.list", {"container": self._container})

    _raw_chk = typchk.Checker(
        {
            "container": int,
            "command": {
                "command": str,
                "arguments": typchk.Any(),
                "queue": typchk.Or(str, typchk.IsNone()),
                "max_time": typchk.Or(int, typchk.IsNone()),
                "stream": bool,
                "tags": typchk.Or([str], typchk.IsNone()),
                "id": typchk.Or(str, typchk.IsNone()),
                "recurring_period": typchk.Or(int, typchk.IsNone()),
            },
        }
    )

    def __init__(self, client, container):
        super().__init__(client.timeout)
        self._client = client
        self._container = container
        self._zerotier = ContainerClient.ContainerZerotierManager(client, container)  # not (self) we use core0 client
        self._flist = FlistManager(client=client, container_id=container)

    @property
    def container(self):
        """
        :return: container id
        """
        return self._container

    @property
    def zerotier(self):
        """
        information about zerotier id
        :return:
        """
        return self._zerotier

    @property
    def flist(self):
        return self._flist

    def raw(
        self, command, arguments, queue=None, max_time=None, stream=False, tags=None, id=None, recurring_period=None
    ):
        """
        Implements the low level command call, this needs to build the command structure
        and push it on the correct queue.

        :param command: Command name to execute supported by the node (ex: core.system, info.cpu, etc...)
                        check documentation for list of built in commands
        :param arguments: A dict of required command arguments depends on the command name.
        :param queue: command queue (commands on the same queue are executed sequentially)
        :param max_time: kill job server side if it exceeded this amount of seconds
        :param stream: If True, process stdout and stderr are pushed to a special queue (stream:<id>) so
            client can stream output
        :param tags: job tags
        :param id: job id. Generated if not supplied
        :param recurring_period: If set, the command execution is rescheduled to execute repeatedly, waiting for recurring_period seconds between each execution.
        :return: Response object
        """
        args = {
            "container": self._container,
            "command": {
                "command": command,
                "arguments": arguments,
                "queue": queue,
                "max_time": max_time,
                "stream": stream,
                "tags": tags,
                "id": id,
                "recurring_period": recurring_period,
            },
        }

        # check input
        self._raw_chk.check(args)

        response = self._client.raw("corex.dispatch", args)

        result = response.get()
        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to dispatch command to container: %s" % result.data)

        cmd_id = json.loads(result.data)
        return self._client.response_for(cmd_id)


class ContainerManager:
    _nic = {
        "type": typchk.Enum("default", "bridge", "zerotier", "vlan", "vxlan", "macvlan", "passthrough"),
        "id": typchk.Or(str, typchk.Missing()),
        "name": typchk.Or(str, typchk.Missing()),
        "hwaddr": typchk.Or(str, typchk.Missing()),
        "config": typchk.Or(
            typchk.Missing(),
            {
                "dhcp": typchk.Or(bool, typchk.IsNone(), typchk.Missing()),
                "cidr": typchk.Or(str, typchk.IsNone(), typchk.Missing()),
                "gateway": typchk.Or(str, typchk.IsNone(), typchk.Missing()),
                "dns": typchk.Or([str], typchk.IsNone(), typchk.Missing()),
            },
        ),
        "monitor": typchk.Or(bool, typchk.Missing()),
    }

    _create_chk = typchk.Checker(
        {
            "root": str,
            "mount": typchk.Or(typchk.Map(str, str), typchk.IsNone()),
            "host_network": bool,
            "nics": [_nic],
            "port": typchk.Or(typchk.Map(int, int), typchk.Map(str, int), typchk.IsNone()),
            "privileged": bool,
            "hostname": typchk.Or(str, typchk.IsNone()),
            "config": typchk.Or(typchk.IsNone(), typchk.Map(str, str)),
            "storage": typchk.Or(str, typchk.IsNone()),
            "name": typchk.Or(str, typchk.IsNone()),
            "identity": typchk.Or(str, typchk.IsNone()),
            "env": typchk.Or(typchk.IsNone(), typchk.Map(str, str)),
            "cgroups": typchk.Or(
                typchk.IsNone(), [typchk.Length((str,), 2, 2)]  # array of (str, str) tuples i.e [(subsyste, name), ...]
            ),
        }
    )

    _layer_chk = typchk.Checker({"container": int, "flist": str})

    _client_chk = typchk.Checker(typchk.Or(int, str))

    _nic_add = typchk.Checker({"container": int, "nic": _nic})

    _nic_remove = typchk.Checker({"container": int, "index": int})

    _portforward_chk = typchk.Checker({"container": int, "host_port": str, "container_port": int})

    DefaultNetworking = object()

    def __init__(self, client):
        self._client = client

    def create(
        self,
        root_url,
        mount=None,
        host_network=False,
        nics=DefaultNetworking,
        port=None,
        hostname=None,
        privileged=False,
        storage=None,
        name=None,
        tags=None,
        identity=None,
        env=None,
        cgroups=None,
        config=None,
    ):
        """
        Creater a new container with the given root flist, mount points and
        zerotier id, and connected to the given bridges
        :param root_url: The root filesystem flist
        :param mount: a dict with {host_source: container_target} mount points.
                      where host_source directory must exists.
                      host_source can be a url to a flist to mount.
        :param host_network: Specify if the container should share the same network stack as the host.
                             if True, container creation ignores both zerotier, bridge and ports arguments below. Not
                             giving errors if provided.
        :param nics: Configure the attached nics to the container
                     each nic object is a dict of the format
                     {
                        'type': nic_type # one of default, bridge, zerotier, macvlan, passthrough, vlan, or vxlan (note, vlan and vxlan only supported by ovs)
                        'id': id # depends on the type
                            bridge: bridge name,
                            zerotier: network id,
                            macvlan: the parent link name,
                            passthrough: the link name,
                            vlan: the vlan tag,
                            vxlan: the vxlan id
                        'name': name of the nic inside the container (ignored in zerotier type)
                        'hwaddr': Mac address of nic.
                        'config': { # config is only honored for bridge, vlan, and vxlan types
                            'dhcp': bool,
                            'cidr': static_ip # ip/mask
                            'gateway': gateway
                            'dns': [dns]
                        }
                     }
        :param port: A dict of host_port: container_port pairs (only if default networking is enabled)
                       Example:
                        `port={8080: 80, 7000:7000}`
                       Source Format: NUMBER, IP:NUMBER, IP/MAST:NUMBER, or DEV:NUMBER
                       Check https://github.com/threefoldtech/0-core/blob/development/docs/networking/portforwards.md for full syntax
        :param hostname: Specific hostname you want to give to the container.
                         if None it will automatically be set to core-x,
                         x beeing the ID of the container
        :param privileged: If true, container runs in privileged mode.
        :param storage: A Url to the ardb storage to use to mount the root flist (or any other mount that requires g8fs)
                        if not provided, the default one from core0 configuration will be used.
        :param name: Optional name for the container
        :param identity: Container Zerotier identity, Only used if at least one of the nics is of type zerotier
        :param env: a dict with the environment variables needed to be set for the container
        :param cgroups: custom list of cgroups to apply to this container on creation. formated as [(subsystem, name), ...]
                        please refer to the cgroup api for more detailes.
        :param config: a map with the config file path as a key and content as a value. This only works when creating a VM from an flist. The
                config files are written to the machine before booting.
                Example:
                config = {'/root/.ssh/authorized_keys': '<PUBLIC KEYS>'}
        """

        if nics == self.DefaultNetworking:
            nics = [{"type": "default"}]
        elif nics is None:
            nics = []

        config = config or {}

        args = {
            "root": root_url,
            "mount": mount,
            "host_network": host_network,
            "nics": nics,
            "port": port,
            "hostname": hostname,
            "privileged": privileged,
            "storage": storage,
            "name": name,
            "identity": identity,
            "env": env,
            "cgroups": cgroups,
            "config": config,
        }

        # validate input
        self._create_chk.check(args)

        response = self._client.raw("corex.create", args, tags=tags)

        return JSONResponse(response)

    def layer(self, container, flist):
        """
        Layer one (and only one) flist on top of the root flist of the given container
        The layering is done in runtime, no pause or restart of the container is needed

        The layer can be called multiple times, each call will only replace the last layer
        with the passed flist
        """
        args = {"container": container, "flist": flist}

        self._layer_chk.check(args)
        return self._client.json("corex.flist-layer", args)

    def list(self):
        """
        List running containers
        :return: a dict with {container_id: <container info object>}
        """
        return self._client.json("corex.list", {})

    def get(self, name):
        """
        Get a container with the given name
        """
        args = {"query": name}
        return self._client.json("corex.get", args)

    def find(self, *tags):
        """
        Find containers that matches set of tags
        :param tags:
        :return:
        """
        tags = list(map(str, tags))
        return self._client.json("corex.find", {"tags": tags})

    def terminate(self, container):
        """
        Terminate a container given it's id

        :param container: container id
        :return:
        """
        self._client_chk.check(container)
        args = {"container": int(container)}
        response = self._client.raw("corex.terminate", args)

        result = response.get()
        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to terminate container: %s" % result.data)

    def nic_add(self, container, nic):
        """
        Hot plug a nic into a container

        :param container: container ID
        :param nic: {
                        'type': nic_type # one of default, bridge, zerotier, macvlan, passthrough, vlan, or vxlan (note, vlan and vxlan only supported by ovs)
                        'id': id # depends on the type
                            bridge: bridge name,
                            zerotier: network id,
                            macvlan: the parent link name,
                            passthrough: the link name,
                            vlan: the vlan tag,
                            vxlan: the vxlan id
                        'name': name of the nic inside the container (ignored in zerotier type)
                        'hwaddr': Mac address of nic.
                        'config': { # config is only honored for bridge, vlan, and vxlan types
                            'dhcp': bool,
                            'cidr': static_ip # ip/mask
                            'gateway': gateway
                            'dns': [dns]
                        }
                     }
        :return:
        """
        args = {"container": container, "nic": nic}
        self._nic_add.check(args)

        return self._client.json("corex.nic-add", args)

    def nic_remove(self, container, index):
        """
        Hot unplug of nic from a container

        Note: removing a nic, doesn't remove the nic from the container info object, instead it sets it's state
        to `destroyed`.

        :param container: container ID
        :param index: index of the nic as returned in the container object info (as shown by container.list())
        :return:
        """
        args = {"container": container, "index": index}
        self._nic_remove.check(args)

        return self._client.json("corex.nic-remove", args)

    def client(self, container):
        """
        Return a client instance that is bound to that container.

        :param container: container id
        :return: Client object bound to the specified container id
        Return a ContainerResponse from container.create
        """

        self._client_chk.check(container)
        return ContainerClient(self._client, int(container))

    def backup(self, container, url):
        """
        Backup a container to the given restic url
        all restic urls are supported

        :param container:
        :param url: Url to restic repo
                examples
                (file:///path/to/restic/?password=<password>)

        :return: Json response to the backup job (do .get() to get the snapshot ID
        """

        args = {"container": container, "url": url}

        return JSONResponse(self._client.raw("corex.backup", args))

    def restore(self, url, tags=None):
        """
        Full restore of a container backup. This restore method will recreate
        an exact copy of the backedup container (including same network setup, and other
        configurations as defined by the `create` method.

        To just restore the container data, and use new configuration, use the create method instead
        with the `root_url` set to `restic:<url>`

        :param url: Snapshot url, the snapshot ID is passed as a url fragment
                    examples:
                        `file:///path/to/restic/repo?password=<password>#<snapshot-id>`
        :param tags: this will always override the original container tags (even if not set)
        :return:
        """
        args = {"url": url}

        return JSONResponse(self._client.raw("corex.restore", args, tags=tags))

    def add_portforward(self, container, host_port, container_port):
        """
        Add portforward from host to kvm container
        :param container: id of the container
        :param host_port: port on host to forward from (string)
                          format: NUMBER, IP:NUMBER, IP/MAST:NUMBER, or DEV:NUMBER
        :param container_port: port on container to forward to
        :return:
        """
        if isinstance(host_port, int):
            host_port = str(host_port)

        args = {"container": container, "host_port": host_port, "container_port": container_port}
        self._portforward_chk.check(args)

        return self._client.json("corex.portforward-add", args)

    def remove_portforward(self, container, host_port, container_port):
        """
        Remove portforward from host to kvm container
        :param container: id of the container
        :param host_port: port on host forwarded from
        :param container_port: port on container forwarded to
        :return:
        """
        if isinstance(host_port, int):
            host_port = str(host_port)

        args = {"container": container, "host_port": host_port, "container_port": container_port}
        self._portforward_chk.check(args)

        return self._client.json("corex.portforward-remove", args)
