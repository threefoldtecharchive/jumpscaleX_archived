
import time
import os

from redis._compat import nativestr

from Jumpscale import j

from core.InstallTools import Redis

class RedisFactory(j.application.JSBaseClass):

    """
    """

    __jslocation__ = "j.clients.redis"

    def _init(self):
        self._cache_clear()

        #

    def _cache_clear(self):
        '''
        clear the cache formed by the functions get() and getQueue()

        '''
        self._redis = {}
        self._redisq = {}
        self._config = {}


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

        :param ipaddr: used to form the key when no unixsocket, defaults to "localhost"
        :type ipaddr: str, optional
        :param port: used to form the key when no unixsocket, defaults to 6379
        :type port: int, optional
        :param password: defaults to ""
        :type password: str, optional
        :param fromcache: if False, will create a new one instead of checking cache, defaults to True
        :type fromcache: bool, optional
        :param unixsocket: path of unixsocket to be used while creating Redis, defaults to None
        :type unixsocket: [type], optional

        :param ssl_certfile: [description], defaults to None
        :type ssl_certfile: [type], optional
        :param ssl_keyfile: [description], defaults to None
        :type ssl_keyfile: [type], optional
        :param timeout: [description], defaults to 10
        :type timeout: int, optional
        :param ping: [description], defaults to True
        :type ping: bool, optional
        :param die: [description], defaults to True
        :type die: bool, optional

        other arguments to redis: ssl_cert_reqs=None, ssl_ca_certs=None

        set_patch is needed when using the client for gedis

        """

        if ipaddr and port:
            key = "%s_%s" % (ipaddr, port)
        else:
            assert unixsocket is not None
            key = unixsocket

        if key not in self._redis or not fromcache:
            if ipaddr and port:
                self._log_debug("REDIS:%s:%s" % (ipaddr, port))
                self._redis[key] = Redis(ipaddr, port, password=password, ssl=ssl, ssl_certfile=ssl_certfile,
                                         ssl_keyfile=ssl_keyfile,unix_socket_path=unixsocket,
                                         # socket_timeout=timeout,
                                         **args)
            else:
                self._log_debug("REDIS:%s" % unixsocket)
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

    def queue_get(self, key, redisclient=None, fromcache=True):

        if redisclient is None:
            redisclient = j.core.db

        if "host" not in redisclient.connection_pool.connection_kwargs:
            ipaddr = redisclient.connection_pool.connection_kwargs["path"]
            port = 0
        else:
            ipaddr = redisclient.connection_pool.connection_kwargs["host"]
            port = redisclient.connection_pool.connection_kwargs["port"]

        # if not fromcache:
        #     return RedisQueue(self.get(ipaddr, port, fromcache=False), name, namespace=namespace)
        key = "%s_%s_%s" % (ipaddr, port, key)
        if fromcache == False or key not in self._redisq:
            self._redisq[key] = redisclient.queue_get(key)
        return self._redisq[key]


    def core_get(self, reset=False, tcp=True):
        """

        js_shell 'j.clients.redis.core_get(reset=False)'

        will try to create redis connection to {DIR_TEMP}/redis.sock or /sandbox/var/redis.sock  if sandbox
        if that doesn't work then will look for std redis port
        if that does not work then will return None


        :param tcp, if True then will also start tcp port on localhost on 6379


        :param reset: stop redis, defaults to False
        :type reset: bool, optional
        :raises RuntimeError: redis couldn't be started
        :return: redis instance
        :rtype: Redis
        """

        if reset:
            self.core_stop()

        if j.core.db and j.core.db.ping() and j.core._db_fakeredis is False:
            return j.core.db

        if not self.core_running(tcp=tcp):
            j.core._db = None
            self._core_start(tcp=tcp)

        # nr = 0
        # while True:
        #     if j.core.db and j.core.db.ping() and j.core._db_fakeredis is False:
        #         return j.core.db
        #
        #     self._log_info("try to connect to redis on unixsocket or tcp port 6379")
        #
        #     nr+=1
        #
        #     if nr > 20:
        #         raise RuntimeError("could not start redis")
        #     time.sleep(0.1)

        return j.core._db

    def core_stop(self):
        '''
        kill core redis

        :raises RuntimeError: redis wouldn't be stopped
        :return: True if redis is not running
        :rtype: bool
        '''
        j.core._db = None
        j.sal.process.execute("redis-cli -s %s shutdown" % self.unix_socket_path, die=False, showout=False)
        j.sal.process.execute("redis-cli shutdown", die=False, showout=False)
        nr = 0
        while True:
            if not self.core_running():
                return True
            if nr > 200:
                raise RuntimeError("could not stop redis")
            time.sleep(0.05)


    def core_running(self,tcp=True):

        '''
        Get status of redis whether it is currently running or not

        :raises e: did not answer
        :return: True if redis is running, False if redis is not running
        :rtype: bool
        '''

        try:
            r = self.get(unixsocket=self.unix_socket_path)
            return r.ping()
        except Exception as e:
            pass

        if tcp and j.sal.nettools.tcpPortConnectionTest("localhost", 6379):
            r = self.get(ipaddr="localhost", port=6379)
            return r.ping()

        return False


    def _core_start(self, tcp=True, timeout=20, reset=False):

        """
        js_shell "j.clients.redis.core_get(reset=True)"

        installs and starts a redis instance in separate ProcessLookupError
        when not in sandbox:
                standard on {DIR_TEMP}/redis.sock
        in sandbox will run in:
            /sandbox/var/redis.sock

        :param timeout:  defaults to 20
        :type timeout: int, optional
        :param reset: reset redis, defaults to False
        :type reset: bool, optional
        :raises RuntimeError: redis server not found after install
        :raises RuntimeError: platform not supported for start redis
        :raises j.exceptions.Timeout: Couldn't start redis server
        :return: redis instance
        :rtype: Redis
        """

        if reset == False:
            if self.core_running(tcp=tcp):
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



        cmd = "mkdir -p /sandbox/var;redis-server --unixsocket /sandbox/var/redis.sock " \
              "--port 6379 " \
              "--maxmemory 100000000 --daemonize yes"

        self._log_info(cmd)
        j.sal.process.execute(cmd)
        limit_timeout = time.time() + timeout
        while time.time() < limit_timeout:
            if self.core_running():
                break
            time.sleep(0.1)
        else:
            raise j.exceptions.Timeout("Couldn't start redis server")

        j.core._db = None

    def test(self, name=""):
        """
        it's run all tests
        js_shell 'j.clients.redis.test()'

        """
        self._test_run(name=name)
