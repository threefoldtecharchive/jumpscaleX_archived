from Jumpscale import j
import json
from gevent.pool import Pool
from gevent import time, signal
import gevent
from gevent.server import StreamServer
from redis.exceptions import ConnectionError
from DigitalMe.servers.gedis.protocol import RedisResponseWriter, RedisCommandParser

JSBASE = j.application.JSBaseClass


class RedisServer(j.application.JSBaseClass):
    def _init2(self, bcdb=None, addr="localhost", port=6380, secret="123456"):
        self.bcdb = bcdb
        self._sig_handler = []
        #
        self.host = addr
        self.port = port  # 1 port higher than the std port
        self.secret = secret
        self.ssl = False
        # j.clients.redis.core_check()  #need to make sure we have a core redis

        if self.bcdb.models is None:
            raise RuntimeError("models are not filled in")

        self.init()

    def init(self):
        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))
        if self.ssl:
            self.ssl_priv_key_path, self.ssl_cert_path = self.sslkeys_generate()
            # Server always supports SSL
            # client can use to talk to it in SSL or not
            self.redis_server = StreamServer(
                (self.host, self.port),
                spawn=Pool(),
                handle=self.handle_redis,
                keyfile=self.ssl_priv_key_path,
                certfile=self.ssl_cert_path,
            )
        else:
            self.redis_server = StreamServer(
                (self.host, self.port), spawn=Pool(), handle=self.handle_redis
            )

    def start(self):
        print("RUNNING")
        print(self)
        self.redis_server.serve_forever()

    def stop(self):
        """
        stop receiving requests and close the server
        """
        # prevent the signal handler to be called again if
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        self._log_info("stopping server")
        self.redis_server.stop()

    def handle_redis(self, socket, address):

        parser = RedisCommandParser(socket)
        response = RedisResponseWriter(socket)

        try:
            self._handle_redis(socket, address, parser, response)
        except ConnectionError as err:
            self._log_info("connection error: {}".format(str(err)))
        finally:
            parser.on_disconnect()
            self._log_info("close connection from {}".format(address))

    def _handle_redis(self, socket, address, parser, response):

        self._log_info("connection from {}".format(address))
        socket.namespace = "system"

        while True:
            request = parser.read_request()

            if request is None:
                self._log_debug("connection lost or tcp test")
                break

            if not request:  # empty list request
                self._log_debug("EMPTYLIST")
                continue

            cmd = request[0]
            redis_cmd = cmd.decode("utf-8").lower()

            if redis_cmd == "command":
                response.encode("OK")
                continue

            elif redis_cmd == "ping":
                response.encode("PONG")
                continue

            elif redis_cmd == "info":
                self.info_internal(response)
                continue

            elif redis_cmd == "select":
                if request[1] == b"0":
                    response.encode("OK")
                    continue
                response.error("DB index is out of range")
                continue

            elif redis_cmd in ["hscan"]:
                kwargs = parser.request_to_dict(request[3:])
                if not hasattr(self, redis_cmd):
                    raise RuntimeError("COULD NOT FIND COMMAND:%s" % redis_cmd)
                    response.error("COULD NOT FIND COMMAND:%s" % redis_cmd)
                else:
                    method = getattr(self, redis_cmd)
                    start_obj = int(request[2].decode())
                    key = request[1].decode()
                    method(response, key, start_obj, **kwargs)
                continue

            else:
                redis_cmd = request[0].decode().lower()
                args = request[1:] if len(request) > 1 else []
                args = [x.decode() for x in args]

                if redis_cmd == "del":
                    redis_cmd = "delete"
                if not hasattr(self, redis_cmd):
                    response.error("COULD NOT FIND COMMAND:%s" % redis_cmd)
                    return

                method = getattr(self, redis_cmd)
                method(response, *args)

                continue

    def info(self):
        return b"NO INFO YET"

    def auth(self, response, *args, **kwargs):
        # j.shell()
        response.encode("OK")

    def _split(self, key):
        """
        split function used in the "normal" methods
        (len, set, get, del)

        split the key into 3 composant:
        - category: objects or schema
        - url: url of the schema
        - key: actual key of the object

        :param key: full encoded key of an object. e.g: object:schema.url:key
        :type key: str
        :return: tuple of (category, url, key, model)
        :rtype: tuple
        """
        if key.strip() == "":
            raise RuntimeError("key cannot be empty")
        splitted = key.split(":")
        len_splitted = len(splitted)
        m = ""
        if len_splitted == 1:
            cat = splitted[0]
            url = ""
            key = ""
        elif len_splitted == 2:
            cat = splitted[0]
            url = splitted[1]
            key = ""
        elif len_splitted == 3:
            cat = splitted[0]
            url = splitted[1]
            key = splitted[2]
        if url != "":
            # url_normalized = j.core.text.strip_to_ascii_dense(url).replace(".", "_")
            if url in self.bcdb.models:
                m = self.bcdb.model_get(url)

        return (cat, url, key, m)

    def set(self, response, key, val):
        cat, url, key, model = self._split(key)
        if cat == "objects":
            if url == "":
                response.error(
                    "url needs to be known, otherwise cannot set e.g. objects:despiegk.test:new"
                )
                return
            if key == "":
                response.error(
                    "key needs to be known, e.g. objects:despiegk.test:new or in stead of new e.g. 101 (id)"
                )
                return

        if cat == "schemas":
            s = j.data.schema.get(val)
            self.bcdb.model_get_from_schema(s)
            response.encode("OK")
            return

        response.error("cannot set, cat:'%s' not supported" % cat)

    def get(self, response, key):
        cat, url, key, model = self._split(key)
        if model is "":
            raise RuntimeError(
                "did not find model from key, maybe models not loaded:%s" % key
            )

        if url == "":
            response.encode("ok")
            return
        if cat == "info":
            response.encode(self.info())
            return
        elif cat == "schemas":
            if url == "":
                response.encode("")
                return
            if key == "":
                # get content from schema
                response.encode(model.schema.text)
                return
            if url in self.bcdb.models:
                response.encode(self.bcdb.models[url].schema.text)
                return
        response.error("cannot get, cat:'%s' not found" % cat)

    def delete(self, response, key):
        cat, url, key, model = self._split(key)

        if url == "" or cat == "schemas" or model == "":
            # DO NOT DELETE SCHEMAS
            response.encode("0")
            return

        if cat == "objects":
            if key == "" and url != "":
                # cannot delete !!! data stays there
                if model.bcdb.zdbclient is None:
                    model.delete_all()
                nr_deleted = 0
            else:
                nr_deleted = 1
                # FIXME: what happens if the key doesn't exist ?
                # there is no exist method on the model for now
                j.shell()
                model.delete(key)
            response.encode(nr_deleted)
            return

        response.error("cannot delete, cat:'%s' not found" % cat)

    def scan(self, response, startid, match="*", count=10000, *args):
        """

        :param scan: id to start from
        :param match: default *
        :param count: nr of items per page
        :return:
        """
        # in first version will only do 1 page, so ignore scan
        res = []

        if len(self.bcdb.models) > 0:
            for url, model in self.bcdb.models.items():
                res.append("schemas:%s" % url)
                res.append("objects:%s" % url)
        else:
            res.append("schemas")
            res.append("objects")
        res.append("info")
        response._array(["0", res])

    def hset(self, response, key, id, val):
        cat, url, _, model = self._split(key)
        if cat != "objects":
            response.error("category %s not valid" % cat)
            return
        if url == "":
            response.error(
                "url needs to be known, otherwise cannot set e.g. objects:despiegk.test:new"
            )
            return
        if key == "":
            response.error(
                "key needs to be known, e.g. objects:despiegk.test:new or in stead of new e.g. 101 (id)"
            )
            return
        if id == "new":
            o = model.set_dynamic(val)
        else:
            id = int(id)
            if id == 0:
                response.error("trying to overwrite first metadata entry, not allowed")
                return
            try:
                o = model.set_dynamic(val, obj_id=id)
            except Exception as e:
                if str(e).find("cannot update object") != -1:
                    response.error(
                        "cannot update object with id:%s, it does not exist" % id
                    )
                    return
                response.error(str(e))
                return

        response.encode("%s" % o.id)

    def hget(self, response, key, id):
        cat, url, _, model = self._split(key)
        if cat != "objects":
            response.error("category %s not valid" % cat)
            return
        if url == "":
            response.error(
                "url needs to be known, otherwise cannot set e.g. objects:despiegk.test:new"
            )
            return
        if key == "":
            response.error(
                "key needs to be known, e.g. objects:despiegk.test:new or in stead of new e.g. 101 (id)"
            )
            return

        obj = model.get(int(id))
        if obj is not None:
            response.encode(obj._json)
        else:
            response.encode(None)

    def hdel(self, response, key, id):
        cat, url, _, model = self._split(key)
        if cat != "objects":
            response.error("category %s not valid" % cat)
            return
        if url == "":
            response.error(
                "url needs to be known, otherwise cannot set e.g. objects:despiegk.test:new"
            )
            return
        if key == "":
            response.error(
                "key needs to be known, e.g. objects:despiegk.test:new or in stead of new e.g. 101 (id)"
            )
            return

        if id == "":
            nr_deleted = model.destroy()
        else:
            nr_deleted = 1
            # FIXME: what happens if the id doesn't exist ?
            # there is no exist method on the model for now
            model.delete(int(id))
        response.encode(nr_deleted)

    def hlen(self, response, key):
        cat, url, _, model = self._split(key)

        if cat != "objects":
            response.error("category %s not valid" % cat)
            return

        if url == "" or cat == "schemas" or model == "":
            response.encode(0)
            return
        response.encode(len(model.get_all()))
        return

    def ttl(self, response, key):
        response.encode("-1")

    def type(self, response, type):
        """
        :param type: is the key we need to give type for
        :return:
        """
        cat, url, key, model = self._split(type)
        if key == "" and url != "":
            # then its hset
            response.encode("hash")
        else:
            response.encode("string")

    def _urls(self):
        urls = [i for i in self.bcdb.models.keys()]
        return urls

    def hscan(self, response, key, startid, count=10000):
        res = []
        response._array(["0", res])

    def info_internal(self, response):
        C = """
        # Server
        redis_version:4.0.11
        redis_git_sha1:00000000
        redis_git_dirty:0
        redis_build_id:13f90e3a88f770eb
        redis_mode:standalone
        os:Darwin 17.7.0 x86_64
        arch_bits:64
        multiplexing_api:kqueue
        atomicvar_api:atomic-builtin
        gcc_version:4.2.1
        process_id:93263
        run_id:49afb34b519a889778562b7addb5723c8c45bec4
        tcp_port:6380
        uptime_in_seconds:3600
        uptime_in_days:1
        hz:10
        lru_clock:12104116
        executable:/Users/despiegk/redis-server
        config_file:

        # Clients
        connected_clients:1
        client_longest_output_list:0
        client_biggest_input_buf:0
        blocked_clients:52

        # Memory
        used_memory:11436720
        used_memory_human:10.91M
        used_memory_rss:10289152
        used_memory_rss_human:9.81M
        used_memory_peak:14691808
        used_memory_peak_human:14.01M
        used_memory_peak_perc:77.84%
        used_memory_overhead:2817866
        used_memory_startup:980704
        used_memory_dataset:8618854
        used_memory_dataset_perc:82.43%
        total_system_memory:17179869184
        total_system_memory_human:16.00G
        used_memory_lua:37888
        used_memory_lua_human:37.00K
        maxmemory:100000000
        maxmemory_human:95.37M
        maxmemory_policy:noeviction
        mem_fragmentation_ratio:0.90
        mem_allocator:libc
        active_defrag_running:0
        lazyfree_pending_objects:0

        # Persistence
        loading:0
        rdb_changes_since_last_save:66381
        rdb_bgsave_in_progress:0
        rdb_last_save_time:1538289882
        rdb_last_bgsave_status:ok
        rdb_last_bgsave_time_sec:-1
        rdb_current_bgsave_time_sec:-1
        rdb_last_cow_size:0
        aof_enabled:0
        aof_rewrite_in_progress:0
        aof_rewrite_scheduled:0
        aof_last_rewrite_time_sec:-1
        aof_current_rewrite_time_sec:-1
        aof_last_bgrewrite_status:ok
        aof_last_write_status:ok
        aof_last_cow_size:0

        # Stats
        total_connections_received:627
        total_commands_processed:249830
        instantaneous_ops_per_sec:0
        total_net_input_bytes:22576788
        total_net_output_bytes:19329324
        instantaneous_input_kbps:0.01
        instantaneous_output_kbps:6.20
        rejected_connections:2
        sync_full:0
        sync_partial_ok:0
        sync_partial_err:0
        expired_keys:5
        expired_stale_perc:0.00
        expired_time_cap_reached_count:0
        evicted_keys:0
        keyspace_hits:76302
        keyspace_misses:3061
        pubsub_channels:0
        pubsub_patterns:0
        latest_fork_usec:0
        migrate_cached_sockets:0
        slave_expires_tracked_keys:0
        active_defrag_hits:0
        active_defrag_misses:0
        active_defrag_key_hits:0
        active_defrag_key_misses:0

        # Replication
        role:master
        connected_slaves:0
        master_replid:49bcd83fa843f4e6657440b7035a1c2314766ac4
        master_replid2:0000000000000000000000000000000000000000
        master_repl_offset:0
        second_repl_offset:-1
        repl_backlog_active:0
        repl_backlog_size:1048576
        repl_backlog_first_byte_offset:0
        repl_backlog_histlen:0

        # CPU
        used_cpu_sys:101.39
        used_cpu_user:64.27
        used_cpu_sys_children:0.00
        used_cpu_user_children:0.00

        # Cluster
        cluster_enabled:0

        # Keyspace
        # db0:keys=10000,expires=1,avg_ttl=7801480
        """
        C = j.core.text.strip(C)
        response.encode(C)
