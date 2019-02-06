
from Jumpscale import j
import redis

JSBASE = j.application.JSBaseClass


class ZDBClientBase(j.application.JSBaseClass):

    def __init__(self, addr="localhost", port=9900, mode="seq", secret="", nsname="test", admin=False):
        """ is connection to ZDB

        port {[int} -- (default: 9900)
        mode -- user,seq(uential) see
                    https://github.com/rivine/0-db/blob/master/README.md
        """
        JSBASE.__init__(self)
        if admin:
            nsname="default"
        self.admin = admin
        self.addr = addr
        self.port = int(port)
        self.mode = mode
        self.secret = secret
        self.type = "ZDB"


        self.redis = _patch_redis_client(j.clients.redis.get(ipaddr=addr, port=port, fromcache=False,  ping=False))

        self.nsname = nsname.lower().strip()

        self._logger_enable()



        if not admin:
        #     #only passwd in admin mode !
        #     self.redis = _patch_redis_client(j.clients.redis.get(ipaddr=addr, port=port, fromcache=False,
        #                                                                 password=self.admin_secret,ping=False))
        # else:


            if self.nsname in ["default","system"]:
                raise RuntimeError("a non admin namespace cannot be default or system")

            #DO NOT AUTOMATICALLY CREATE THE NAMESPACE !!!!!
            #only go inside namespace if not in admin mode
            if self.secret is "":
                self._logger.debug("select namespace:%s with NO secret" % (self.nsname))
                self.redis.execute_command("SELECT", self.nsname)
            else:
                self._logger.debug("select namespace:%s with a secret" % (self.nsname))
                self.redis.execute_command("SELECT", self.nsname, self.secret)


        assert self.ping()

    def _key_encode(self, key):
        return key

    def _key_decode(self, key):
        return key

    def set(self, data, key=None):
        if key is None:
            key = ''
        return self.redis.execute_command("SET", key, data)

    def get(self, key):
        return self.redis.execute_command("GET", key)

    def exists(self, key):
        return self.redis.execute_command("EXISTS", key) == 1

    def delete(self, key):
        if not key:
            raise ValueError("key must be provided")
        self.redis.execute_command("DEL", key)

    def flush(self,meta=None):
        """
        will remove all data from the database DANGEROUS !!!!
        :return:
        """
        if meta:
            data = meta._data
            self.redis.execute_command("FLUSH")
            #recreate the metadata table
            meta.reset()
            #copy the old data back
            meta._data=data
            #now make sure its back in the db
            meta.save()
        else:
            self.redis.execute_command("FLUSH")

    @property
    def nsinfo(self):
        cmd = self.redis.execute_command("NSINFO", self.nsname)
        return _parse_nsinfo(cmd.decode())

    def list(self, key_start=None, reverse=False):
        """
        list all the keys in the namespace

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                        if False, walk from older to newer keys
                        if True walk from newer to older keys
                        defaults to False
        :param reverse: bool, optional
        :return: list of keys
        :rtype: [str]
        """
        result = []
        for key, data in self.iterate(key_start=key_start, reverse=reverse, keyonly=True):
            result.append(key)
        return result

    def iterate(self, key_start=None, reverse=False, keyonly=False):
        """
        walk over all the namespace and yield (key,data) for each entries in a namespace

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                if False, walk from older to newer keys
                if True walk from newer to older keys
                defaults to False
        :param reverse: bool, optional
        :param keyonly: [description], defaults to False
        :param keyonly: bool, optional
        :raises e: [description]
        """

        next = None
        data = None

        if key_start is not None:
            next = self.redis.execute_command("KEYCUR", self._key_encode(key_start))
            if not keyonly:
                data = self.get(key_start)
            yield (key_start, data)

        CMD = "SCANX" if not reverse else "RSCAN"

        while True:
            try:
                if not next:
                    response = self.redis.execute_command(CMD)
                else:
                    response = self.redis.execute_command(CMD, next)
                # format of the response
                # see https://github.com/threefoldtech/0-db/tree/development#scan
            except redis.ResponseError as e:
                if e.args[0] == 'No more data':
                    return
                raise e

            (next, results) = response
            for item in results:
                keyb, size, epoch = item
                key_new = self._key_decode(keyb)
                data = None
                if not keyonly:
                    data = self.redis.execute_command("GET", keyb)
                yield (key_new, data)

    @property
    def count(self):
        """
        :return: return the number of entries in the namespace
        :rtype: int
        """
        return self.nsinfo['entries']




    def ping(self):
        """
        go to default namespace & ping
        :return:
        """
        return self.redis.ping()

def _patch_redis_client(redis):
    # don't auto parse response for set, it's not 100% redis compatible
    # 0-db does return a key after in set
    for cmd in ['SET', 'DEL']:
        if cmd in redis.response_callbacks:
            del redis.response_callbacks[cmd]
    return redis

def _parse_nsinfo(raw):
    def empty(line):
        line = line.strip()
        if len(line) <= 0 or \
                line[0] == "#" or \
                ":" not in line:
            return False
        return True

    info = {}
    for line in filter(empty, raw.splitlines()):
        key, val = line.split(":")
        try:
            val = int(val)
            info[key] = val
            continue
        except ValueError:
            pass
        try:
            val = float(val)
            info[key] = val
            continue
        except ValueError:
            pass

        info[key] = str(val).strip()
    return info
