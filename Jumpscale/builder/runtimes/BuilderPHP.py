from Jumpscale import j
import textwrap
from copy import deepcopy

builder_method = j.builder.system.builder_method

compileconfig = {}
compileconfig["enable_mbstring"] = True
compileconfig["with_zip"] = True
compileconfig["enable_gd"] = True
compileconfig["with_curl"] = True  # apt-get install libcurl4-openssl-dev libzip-dev
compileconfig["with_libzip"] = False
compileconfig["with_zlib"] = True
compileconfig["with_openssl"] = True
compileconfig["enable_fpm"] = True
compileconfig["prefix"] = "/sandbox"
compileconfig["exec_prefix"] = "/sandbox"
compileconfig["with_mysqli"] = True
compileconfig["with_pdo_mysql"] = True
compileconfig["with_mysql_sock"] = "/var/run/mysqld/mysqld.sock"


class BuilderPHP(j.builder.system._BaseClass):

    NAME = "php-fpm"

    @builder_method()
    def build(self, **config):
        """
        kosmos 'j.builder.runtimes.php.build()'
        :param config:
        :return:
        """
        # install required packages
        pkgs = "curl libxml2-dev libpng-dev libcurl4-openssl-dev libzip-dev zlibc zlib1g zlib1g-dev \
        libmysqld-dev libmysqlclient-dev re2c bison bzip2 build-essential libaprutil1-dev libapr1-dev \
        openssl pkg-config libssl-dev file libreadline7 libreadline-dev libzip4 autoconf libtool libsqlite3-dev"
        self.system.package.install(pkgs)

        # install oniguruma
        C = """
        cd {DIR_BUILD}
        rm -rf oniguruma
        git clone https://github.com/kkos/oniguruma.git --depth 1
        cd oniguruma
        autoreconf -vfi
        ./configure --prefix=/sandbox
        make
        make install
        """
        self._execute(C)

        # clone php-src repo
        C = """
        cd {DIR_BUILD}
        rm -rf php-src
        git clone https://github.com/php/php-src.git --depth 1
        """
        self._execute(C)

        # configure arguments
        compileconfig["with_apxs2"] = self._replace("{DIR_APPS}/apache2/bin/apxs")
        buildconfig = deepcopy(compileconfig)
        buildconfig.update(config)  # should be defaultconfig.update(config) instead of overriding the explicit ones.

        # check for apxs2 binary if it's valid.
        apxs = buildconfig["with_apxs2"]
        if not self.tools.exists(apxs):
            buildconfig.pop("with_apxs2")

        args_string = ""
        for k, v in buildconfig.items():
            k = k.replace("_", "-")
            if v is True:
                args_string += " --{k}".format(k=k)
            else:
                args_string += " --{k}={v}".format(k=k, v=v)
        args_string = self._replace(args_string)

        # build php
        C = (
            """
        cd {DIR_BUILD}/php-src
        ./buildconf
        export PKG_CONFIG_PATH=/sandbox/lib/pkgconfig/
        ./configure %s
        make
        """
            % args_string
        )
        self._execute(C, timeout=1000)

        # check if we need an php accelerator: https://en.wikipedia.org/wiki/List_of_PHP_accelerators

    @builder_method()
    def install(self):
        fpm_default_conf = """\
        include=/sandbox/etc/php-fpm.d/*.conf
        """
        fpm_www_conf = """\
        ;nobody Start a new pool named 'www'.
        [www]

        ;prefix = /path/to/pools/$pool

        user =  www-data
        group = www-data

        listen = 127.0.0.1:9000

        listen.allowed_clients = 127.0.0.1

        pm = dynamic
        pm.max_children = 5
        pm.start_servers = 2
        pm.min_spare_servers = 1
        pm.max_spare_servers = 3
        """
        fpm_default_conf = textwrap.dedent(fpm_default_conf)
        fpm_www_conf = textwrap.dedent(fpm_www_conf)
        # make sure to save that configuration file ending with .conf under php/etc/php-fpm.d/www.conf
        self._execute("cd {DIR_BUILD}/php-src && make install")

        self.tools.dir_ensure(self._replace("{/sandbox/etc/php-fpm.d"))
        fpm_default_conf = self._replace(fpm_default_conf)
        fpm_www_conf = self._replace(fpm_www_conf)
        self._write(path="/sandbox/etc/php-fpm.conf", txt=fpm_default_conf)
        self._write(path="/sandbox/etc/php-fpm.d/www.conf", txt=fpm_www_conf)

        php_tmp_path = self._replace("{DIR_BUILD}/php-src")
        php_app_path = self._replace("/sandbox")
        self._copy(
            self.tools.joinpaths(php_tmp_path, "php.ini-development"), self.tools.joinpaths(php_app_path, "php.ini")
        )

        # It is important that we prevent Nginx from passing requests to the PHP-FPM backend if the file does not exists,
        # allowing us to prevent arbitrarily script injection.
        # We can fix this by setting the cgi.fix_pathinfo directive to 0 within our php.ini file.
        C = """
        sed -i 's/;cgi.fix_pathinfo=1/;cgi.fix_pathinfo=0/g' {php_app_path}/php.ini
        """.format(
            php_app_path=php_app_path
        )
        self._execute(C)

    @property
    def startup_cmds(self):
        cmd = "/sandbox/sbin/php-fpm -F -y /sandbox/etc/php-fpm.conf"  # foreground
        cmds = [j.tools.startupcmd.get(name=self.NAME, cmd=cmd)]
        return cmds

    def stop(self):
        super().stop()
        j.sal.process.killProcessByName(self.NAME)

    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key="test_main")
