from Jumpscale import tcpPortConnectionTest
import time
import os
import socket
from redis._compat import nativestr
from .RedisQueue import RedisQueue
from .Redis import Redis
from Jumpscale import j

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class RedisFactory(JSConfigBaseFactory):

    """
    """

    __jslocation__ = "j.clients.redis"

    def _init(self):
        self._cache_clear()
        self._logger_enable()

    def _cache_clear(self):
        """
        clear the cache formed by the functions get() and getQueue()
        """
        self._redis = {}
        self._redisq = {}
        self._config = {}

    @property
    def _REDIS_CLIENT_CLASS(self):
        self._logger.debug("REDIS CLASS")
        return Redis

    def get(
            self,
            ipaddr="localhost",
            port=6379,
            password="",
            fromcache=True,
            unixsocket=None,
            ardb_patch=False,
            set_patch=False,
            ssl=False,
            ssl_certfile=None,
            ssl_keyfile=None,
            timeout=10,
            ping=True,
            die=True,
            **args):
        """
        get an instance of redis client, store it in cache so we could easily retrieve it later

        :param ipaddr: used to form the key when no unixsocket
        :param port: used to form the key when no unixsocket
        :param fromcache: if False, will create a new one instead of checking cache
        :param unixsocket: path of unixsocket to be used while creating Redis

        other arguments to redis: ssl_cert_reqs=None, ssl_ca_certs=None 

        set_patch is needed when using the client for gedis

        """

        if unixsocket is None:
            key = "%s_%s" % (ipaddr, port)
        else:
            key = unixsocket

        if key not in self._redis or not fromcache:
            if unixsocket is None:
                self._logger.debug("REDIS:%s:%s" % (ipaddr, port))
                self._redis[key] = Redis(ipaddr, port, password=password, ssl=ssl, ssl_certfile=ssl_certfile,
                                         ssl_keyfile=ssl_keyfile,
                                         # socket_timeout=timeout,
                                         **args)
            else:
                self._logger.debug("REDIS:%s" % unixsocket)
                self._redis[key] = Redis(unix_socket_path=unixsocket,
                                         # socket_timeout=timeout,
                                         password=password,
                                         ssl=ssl, ssl_certfile=ssl_certfile,
                                         ssl_keyfile=ssl_keyfile, **args)

        if ardb_patch:
            self._ardb_patch(self._redis[key])

        if set_patch:
            self._set_patch(self._redis[key])

        if ping:
            try:
                res = self._redis[key].ping()
            except Exception as e:
                if "Timeout" in str(e) or "Connection refused" in str(e):
                    if die == False:
                        return None
                    else:
                        raise RuntimeError("Redis on %s:%s did not answer" % (ipaddr, port))
                else:
                    raise e

        return self._redis[key]

    def _ardb_patch(self, client):
        client.response_callbacks['HDEL'] = lambda r: r and nativestr(r) == 'OK'

    def _set_patch(self, client):
        client.response_callbacks['SET'] = lambda r: r
        client.response_callbacks['DEL'] = lambda r: r

    def queue_get(self, name, redisclient=None, namespace="queues", fromcache=True):
        """
        get an instance of redis queue, store it in cache so we can easily retrieve it later

        :param ipaddr: used to form the key when no unixsocket
        :param port: used to form the key when no unixsocket
        :param name: name of the queue
        :param namespace: value of namespace for the queue
        :param fromcache: if False, will create a new one instead of checking cache
        """
        if "host" not in redisclient.connection_pool.connection_kwargs:
            ipaddr = redisclient.connection_pool.connection_kwargs["path"]
            port = 0
        else:
            ipaddr = redisclient.connection_pool.connection_kwargs["host"]
            port = redisclient.connection_pool.connection_kwargs["port"]

        # if not fromcache:
        #     return RedisQueue(self.get(ipaddr, port, fromcache=False), name, namespace=namespace)
        key = "%s_%s_%s_%s" % (ipaddr, port, name, namespace)
        if fromcache == False or key not in self._redisq:
            self._redisq[key] = RedisQueue(redisclient, name, namespace=namespace)
        return self._redisq[key]

    @property
    def unix_socket_path(self):
        if j.core.isSandbox:
            return '/sandbox/var/redis.sock'
        else:
            return '%s/redis.sock' % j.dirs.TMPDIR

    def core_get(self, reset=False):
        """

        js_shell 'j.clients.redis.core_get(reset=False)'


        will try to create redis connection to {DIR_TEMP}/redis.sock or /sandbox/var/redis.sock  if sandbox
        if that doesn't work then will look for std redis port
        if that does not work then will return None



        """
        if reset:
            self.core_stop()

        if not self.core_running():
            self._core_start()

        nr = 0
        while True:
            self._logger.info("try to connect to redis of unixsocket:%s or tcp port 6379" % self.unix_socket_path)
            if self.core_running():
                return self.get(ipaddr="", port=0, unixsocket=self.unix_socket_path)
            if nr > 200:
                raise RuntimeError("could not start redis")
            time.sleep(0.05)

    def core_stop(self):
        """
        kill core redis
        """
        j.sal.process.execute("redis-cli -s %s shutdown" % self.unix_socket_path, die=False, showout=False)
        j.sal.process.execute("redis-cli shutdown", die=False, showout=False)
        nr = 0
        while True:
            if not self.core_running():
                return True
            if nr > 200:
                raise RuntimeError("could not stop redis")
            time.sleep(0.05)

    def core_running(self):
        if j.core.isSandbox:
            if not j.sal.fs.exists(self.unix_socket_path):
                return False
            try:
                r = self.get(ipaddr="", port=0, unixsocket=self.unix_socket_path)
            except Exception as e:
                if str(e).find("did not answer") != -1:
                    return False
                raise e
            return r.ping()
        else:
            if j.sal.nettools.tcpPortConnectionTest("localhost", 6379) == False:
                r = self.get(ipaddr="localhost", port=6379, unixsocket=self.unix_socket_path)
            return r.ping()
        return False

    def _core_start(self, timeout=20, reset=False):
        """

        js_shell "j.clients.redis.core_get(reset=True)"

        installs and starts a redis instance in separate ProcessLookupError
        when not in sandbox:
                standard on {DIR_TEMP}/redis.sock
        in sandbox will run in:
            /sandbox/var/redis.sock

        """

        if reset == False:
            if self.core_running():
                return self.core_get()

        if not j.core.isSandbox:
            if j.core.platformtype.myplatform.isMac:
                if not j.sal.process.checkInstalled("redis-server"):
                    # prefab.system.package.install('redis')
                    j.sal.process.execute("brew unlink redis", die=False)
                    j.sal.process.execute("brew install redis;brew link redis")
                    if not j.sal.process.checkInstalled("redis-server"):
                        raise RuntimeError("Cannot find redis-server even after install")
                j.sal.process.execute("redis-cli -s %s/redis.sock shutdown" %
                                      j.dirs.TMPDIR, die=False, showout=False)
                j.sal.process.execute("redis-cli shutdown", die=False, showout=False)
            elif j.core.platformtype.myplatform.isLinux:
                if j.core.platformtype.myplatform.isAlpine:
                    os.system("apk add redis")
                elif j.core.platformtype.myplatform.isUbuntu:
                    os.system("apt install redis-server -y")
            else:
                raise RuntimeError("platform not supported for start redis")

        if not j.core.platformtype.myplatform.isMac:
            # cmd = "echo never > /sys/kernel/mm/transparent_hugepage/enabled"
            # os.system(cmd)
            cmd = "sysctl vm.overcommit_memory=1"
            os.system(cmd)

        if reset:
            self.core_stop()
        #
        # if j.core.isSandbox:
        #     cmd_="redis-server /sandbox/cfg/redis.conf"
        #     stopcmd = "redis-cli -s /sandbox/cfg/redis.conf shutdown;rm -f /sandbox/var/redis.sock"
        #     cmd = j.tools.tmux.cmd_get(name="redis",pane="p12",cmd=cmd_,
        #                                stopcmd=stopcmd,
        #                                process_strings=["redis-server"],
        #                                window=tmux_window)
        #     cmd.start(checkrunning=False)
        #
        # else:
        if "TMPDIR" in os.environ:
            tmpdir = os.environ["TMPDIR"]
        else:
            tmpdir = "/tmp"
        cmd = "mkdir -p /sandbox/var;redis-server --unixsocket /sandbox/var/redis.sock " \
              "--port 6379 " \
              "--maxmemory 100000000 --daemonize yes"
        self._logger.info(cmd)
        j.sal.process.execute(cmd)
        limit_timeout = time.time() + timeout
        while time.time() < limit_timeout:
            if self.core_running():
                # if tcpPortConnectionTest("localhost", 6379):
                break
            time.sleep(0.1)
        else:
            raise j.exceptions.Timeout("Couldn't start redis server")
