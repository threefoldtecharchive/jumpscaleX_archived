import json
import socket
import time
import uuid

import redis
from Jumpscale import j

from . import typchk
from .AggregatorManager import AggregatorManager
from .BaseClient import BaseClient, DEFAULT_TIMEOUT
from .BridgeManager import BridgeManager
from .BtrfsManager import BtrfsManager
from .CGroupManager import CGroupManager
from .Config import Config
from .ContainerManager import ContainerManager
from .DiskManager import DiskManager
from .KvmManager import KvmManager
from .LogManager import LogManager
from .Nft import Nft
from .Response import Response
from .RTInfoManager import RTInfoManager
from .WebManager import WebManager
from .ZerotierManager import ZerotierManager
from .ZFSManager import ZFSManager
from .SocatManager import SocatManager
from .PowerManager import PowerManager


class Client(BaseClient):
    _raw_chk = typchk.Checker(
        {
            "id": str,
            "command": str,
            "arguments": typchk.Any(),
            "queue": typchk.Or(str, typchk.IsNone()),
            "max_time": typchk.Or(int, typchk.IsNone()),
            "stream": bool,
            "tags": typchk.Or([str], typchk.IsNone()),
            "recurring_period": typchk.Or(int, typchk.IsNone()),
        }
    )

    def __init__(self, host, port=6379, unixsocket=None, password=None, db=0, ssl=True, timeout=120):
        self.host = host
        self.port = port
        self.unixsocket = unixsocket
        self.password = password
        self.db = db
        self.ssl = ssl
        self.timeout = timeout

        BaseClient.__init__(self, self.timeout)
        self._redis = None

        self._container_manager = ContainerManager(self)
        self._bridge_manager = BridgeManager(self)
        self._disk_manager = DiskManager(self)
        self._btrfs_manager = BtrfsManager(self)
        self._zerotier = ZerotierManager(self)
        self._kvm = KvmManager(self)
        self._log_manager = LogManager(self)
        self._nft = Nft(self)
        self._config_manager = Config(self)
        self._aggregator = AggregatorManager(self)
        self._jwt_expire_timestamp = 0
        self._web = WebManager(self)
        self._rtinfo = RTInfoManager(self)
        self._cgroup = CGroupManager(self)
        self._zfs = ZFSManager(self)
        self._socat = SocatManager(self)
        self._power = PowerManager(self)

    @property
    def power(self):
        return self._power

    @property
    def socat(self):
        return self._socat

    @property
    def redis(self):
        # make sure the jwt token used as password is still valid
        # if not, we try to refresh it and force to re-created the redis connection
        password = self.password

        if password:
            self._jwt_expire_timestamp = j.clients.itsyouonline.jwt_expire_timestamp(password)
        if self._jwt_expire_timestamp and self._jwt_expire_timestamp - 300 < time.time():
            password = j.clients.itsyouonline.jwt_refresh(password, validity=3600)
            self.password = password
            # force recreation of redis connection
            if self._redis:
                self._redis = None
            self._jwt_expire_timestamp = j.clients.itsyouonline.jwt_expire_timestamp(password)

        if self._redis is None:
            if self.unixsocket:
                self._redis = redis.Redis(unix_socket_path=self.unixsocket, db=self.db)
            else:
                timeout = self.timeout
                socket_timeout = (timeout + 5) if timeout else 15
                socket_keepalive_options = dict()
                if hasattr(socket, "TCP_KEEPIDLE"):
                    socket_keepalive_options[socket.TCP_KEEPIDLE] = 1
                if hasattr(socket, "TCP_KEEPINTVL"):
                    socket_keepalive_options[socket.TCP_KEEPINTVL] = 1
                if hasattr(socket, "TCP_KEEPIDLE"):
                    socket_keepalive_options[socket.TCP_KEEPIDLE] = 1

                self._redis = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    ssl=self.ssl,
                    ssl_cert_reqs=None,
                    socket_timeout=socket_timeout,
                    socket_keepalive=True,
                    socket_keepalive_options=socket_keepalive_options,
                )

        return self._redis

    @property
    def zfs(self):
        """
        ZFS manager
        """
        return self._zfs

    @property
    def container(self):
        """
        Container manager
        :return:
        """
        return self._container_manager

    @property
    def bridge(self):
        """
        Bridge manager
        :return:
        """
        return self._bridge_manager

    @property
    def disk(self):
        """
        Disk manager
        :return:
        """
        return self._disk_manager

    @property
    def btrfs(self):
        """
        Btrfs manager
        :return:
        """
        return self._btrfs_manager

    @property
    def zerotier(self):
        """
        Zerotier manager
        :return:
        """
        return self._zerotier

    @property
    def kvm(self):
        """
        KVM manager
        :return:
        """
        return self._kvm

    @property
    def log_manager(self):
        """
        Logger manager
        :return:
        """
        return self._log_manager

    @property
    def nft(self):
        """
        NFT manager
        :return:
        """
        return self._nft

    @property
    def config_manager(self):
        """
        Config manager
        :return:
        """
        return self._config_manager

    @property
    def aggregator(self):
        """
        Aggregator manager
        :return:
        """
        return self._aggregator

    @property
    def web(self):
        """
        Web manager
        :return:
        """
        return self._web

    @property
    def rtinfo(self):
        """
        RTInfo manager
        :return:
        """
        return self._rtinfo

    @property
    def cgroup(self):
        """
        Cgroup manager
        """
        return self._cgroup

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

        if not id:
            id = str(uuid.uuid4())

        payload = {
            "id": id,
            "command": command,
            "arguments": arguments,
            "queue": queue,
            "max_time": max_time,
            "stream": stream,
            "tags": tags,
            "recurring_period": recurring_period,
        }

        self._raw_chk.check(payload)
        flag = "result:{}:flag".format(id)
        self.redis.rpush("core:default", json.dumps(payload))
        if self.redis.brpoplpush(flag, flag, DEFAULT_TIMEOUT) is None:
            TimeoutError("failed to queue job {}".format(id))

        return Response(self, id)

    def response_for(self, id):
        return Response(self, id)
