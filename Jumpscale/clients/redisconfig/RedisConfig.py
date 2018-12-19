from Jumpscale import j


class RedisConfig(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    addr = "127.0.0.1"
    port = 6379
    password_ = ""
    ardb_patch = false
    unixsocket = ""
    set_patch = false
    ssl = false
    sslkey = false
    """    

    def _init(self):
        self._redis = None

    @property
    def ssl_certfile_path(self):
        p = j.sal.fs.getDirName(self.config.path) + "cert.pem"
        if self.sslkey:
            return p

    @property
    def ssl_keyfile_path(self):
        p = j.sal.fs.getDirName(self.config.path) + "key.pem"
        if self.sslkey:
            return p

    @property
    def redis(self):
        if self._redis is None:

            if unixsocket == "":
                unixsocket = None

            self._redis = j.clients.redis.get(
                ipaddr=self.addr, port=self.port, password=self.password,
                unixsocket=self.unixsocket, ardb_patch=self.ardb_patch,
                set_patch=self.set_patch, ssl=self.ssl,
                ssl_keyfile=self.ssl_keyfile, ssl_certfile=self.ssl_certfile,
                ssl_cert_reqs=None, ssl_ca_certs=None)

        return self._redis

    def ssl_keys_save(self, ssl_keyfile, ssl_certfile):
        if j.sal.fs.exists(ssl_keyfile):
            ssl_keyfile = j.sal.fs.readFile(ssl_keyfile)
        if j.sal.fs.exists(ssl_certfile):
            ssl_certfile = j.sal.fs.readFile(ssl_certfile)
        j.sal.fs.writeFile(self.ssl_certfile_path, ssl_certfile)
        j.sal.fs.writeFile(self.ssl_keyfile_path, ssl_keyfile)

    def __str__(self):
        return "redis:%-14s %-25s:%-4s (ssl:%s)" % (self.instance, self.addr,self.port,self.ssl)

    __repr__ = __str__
