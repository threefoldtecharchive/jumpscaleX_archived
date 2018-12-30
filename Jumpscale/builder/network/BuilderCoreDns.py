from Jumpscale import j




class BuilderCoreDns(j.builder.system._BaseClass):
    NAME = "coredns"

    def __init(self):
        self.golang = j.builder.runtimes.golang
        self.coredns_code_dir = self.golang.GOPATHDIR + '/src/github.com/coredns/coredns'
        self.path_config = j.builder.tools.j.core.tools.text_replace("{DIR_CFG}") + "/CoreDNSConfig.json"

    def install(self, zone=".", password=None, reset=False, start=True):
        """
        installs and runs coredns server with redis plugin
        """
        self.__init()

        if self._done_check("install", reset):
            if start:
                self.start()
            return
        # install golang
        j.builder.runtimes.golang.install(reset=reset)

        # install redis
        if not password:
            j.logger.logger.warning("You didn't set a password for redis, that's not secure"
                                    "you shouldn't use this in a production machine")
        j.builder.db.redis.install()
        j.builder.db.redis.start(ip='0.0.0.0', password=password)

        # install coredns
        # get
        # TODO:*3 weird we have to do this
        try:
            self.golang.get(url='github.com/coredns/coredns', install=False)
        except Exception as e:
            if not "github.com/mholt/caddy/startupshutdown" in str(e):
                raise RuntimeError(e)

        plugins_path = self.coredns_code_dir + '/plugin.cfg'
        j.sal.fs.writeFile(plugins_path, self.coredns_plugins)
        # configure coredns
        if password:
            password = "password %s" % password
        else:
            password = ""

        config = """
%s:53 {
    redis {
        address localhost:6379
        %s
        connect_timeout 100
        read_timeout 100
        ttl 360
    }
    errors stdout
    log stdout
}
        """ % (zone, password)
        j.sal.fs.writeFile(
            self.path_config, config, replaceInContent=True)
        # install coredns redis plugin
        cmd = """
        go get github.com/arvancloud/redis
        cd {coredns_code_dir}
        go generate
        go build
        """.format(coredns_code_dir=self.coredns_code_dir)
        j.sal.process.execute(cmd)
        # start coredns

        if start:
            self.start()

        self._done_set('install')

    def start(self):
        self.__init()
        cmd = "{coredns_path}/coredns -conf {path_config}".format(
                coredns_path=self.coredns_code_dir,path_config=self.path_config)
        j.builder.system.processmanager.get().ensure("coredns", cmd, wait=10, expect='53')

    def register_a_record(self, ns_addr, domain_name, subdomain, resolve_to=None,
                          redis_port=6379, redis_password='', ttl=300, override=False):
        """registers an A record on a coredns server through redis connection

        Arguments:
            ns_addr {string} -- dns ip address
            domain_name {string} -- domain to register an A record on
            subdomain {string} -- subdomain to register (hostname)

        Keyword Arguments:
            resolve_to {string} -- target ip, if none will use the machine pub ip (default: {None})
            redis_port {number} -- redis port allowed by the dns server (default: {6379})
            redis_password {string} -- redis password (default: {None})
            ttl {number} -- time to live (default: 300)
            override {boolean} -- if true it will override if A record exists (default: {False})
        """
        self.__init()
        j.builder.tools.package_install("redis-tools")
        if redis_password:
            redis_password = '-a {}'.format(redis_password)

        if redis_port:
            redis_port = '-p {}'.format(redis_port)

        if ns_addr:
            ns_addr = '-h {}'.format(ns_addr)

        command = 'HGET {domain_name} {subdomain}'
        # check connection and check if key exists
        rc, out, _ = j.sal.process.execute('redis-cli {ns_addr} {redis_port} {redis_password} {command}'.format(
            ns_addr=ns_addr, redis_port=redis_port, redis_password=redis_password, command=command))
        if rc != 0:
            raise RuntimeError("Can't connect to {ns_addr} on port {port},"
                               "please make sure that this host is reachable and redis server is running")
        exist = False
        if out:
            exist = True

        if not exist or override:
            a_record = '{"a": [{"ttl": 300, "ip": "%s"}]}' % resolve_to

            # this is a bad hack
            # TODO: handle "" properly in core.run
            command = "HSET {domain_name} {subdomain} '{a_record}'".format(domain_name=domain_name, subdomain=subdomain,
                                                                           a_record=a_record)
            cmd = """
            redis-cli {ns_addr} {redis_port} {redis_password} {command};
            """.format(ns_addr=ns_addr, redis_port=redis_port, redis_password=redis_password, command=command)

            j.sal.fs.writeFile('/tmp/gen.sh', cmd)

            rc, _, err = j.builder.executor._execute_script(
                "bash /tmp/gen.sh")
            if rc != 0:
                raise RuntimeError(err)

    @property
    def coredns_plugins(self):
        plugins = """
        tls:tls
        nsid:nsid
        root:root
        bind:bind
        debug:debug
        trace:trace
        health:health
        pprof:pprof
        prometheus:metrics
        errors:errors
        log:log
        dnstap:dnstap
        chaos:chaos
        loadbalance:loadbalance
        cache:cache
        rewrite:rewrite
        dnssec:dnssec
        autopath:autopath
        template:template
        hosts:hosts
        route53:route53
        federation:federation
        kubernetes:kubernetes
        file:file
        auto:auto
        secondary:secondary
        etcd:etcd
        redis:github.com/arvancloud/redis
        forward:forward
        proxy:proxy
        erratic:erratic
        whoami:whoami
        on:github.com/mholt/caddy/onevent
        """
        return j.core.text.strip(plugins)
