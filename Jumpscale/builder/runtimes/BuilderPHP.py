from Jumpscale import j
import textwrap
from copy import deepcopy


compileconfig = {}
compileconfig['enable_mbstring'] = True
compileconfig['enable_zip'] = True
compileconfig['with_gd'] = True
compileconfig['with_curl'] = True  # apt-get install libcurl4-openssl-dev libzip-dev
compileconfig['with_libzip'] = True
compileconfig['with_zlib'] = True
compileconfig['with_openssl'] = True
compileconfig['enable_fpm'] = True
compileconfig['prefix'] = "{DIR_BASE}/apps/php"
compileconfig['exec_prefix'] = "{DIR_BASE}/apps/php"
compileconfig['with_mysqli'] = True
compileconfig['with_pdo_mysql'] = True
compileconfig['with_mysql_sock'] = "/var/run/mysqld/mysqld.sock"


class BuilderPHP(j.builder.system._BaseClass):

    NAME = 'php'

    def build(self, **config):

        '''
        js_shell 'j.builder.runtimes.php.build()'
        :param config:
        :return:
        '''
        j.tools.bash.local.locale_check()

        if j.core.platformtype.myplatform.isUbuntu:
            pkgs = "libxml2-dev libpng-dev libcurl4-openssl-dev libzip-dev zlibc zlib1g zlib1g-dev \
            libmysqld-dev libmysqlclient-dev re2c bison bzip2 build-essential libaprutil1-dev libapr1-dev \
            openssl pkg-config libssl-dev libsslcommon2-dev file"
            j.sal.ubuntu.apt_update()
            j.sal.ubuntu.apt_install(pkgs, update_md=False)
            
            compileconfig['with_apxs2'] = j.builder.tools.replace("{DIR_BASE}/apps/apache2/bin/apxs")
            buildconfig = deepcopy(compileconfig)
            buildconfig.update(config)  # should be defaultconfig.update(config) instead of overriding the explicit ones.

            # check for apxs2 binary if it's valid.
            apxs = buildconfig['with_apxs2']
            if not j.builder.tools.file_exists(apxs):
                buildconfig.pop('with_apxs2')

            args_string = ""
            for k, v in buildconfig.items():
                k = k.replace("_", "-")
                if v is True:
                    args_string += " --{k}".format(k=k)
                else:
                    args_string += " --{k}={v}".format(k=k, v=v)
            C = """
            set -x
            rm -f {DIR_TEMP}/php-7.3.0.tar.bz*
            cd {DIR_TEMP} && [ ! -f {DIR_TEMP}/php-7.3.0.tar.bz2 ] && wget http://be2.php.net/distributions/php-7.3.0.tar.bz2
            cd {DIR_TEMP} && tar xvjf {DIR_TEMP}/php-7.3.0.tar.bz2
            mv {DIR_TEMP}/php-7.3.0/ {DIR_TEMP}/php

            """

            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)

            C = """cd {DIR_TEMP}/php && ./configure {args_string}""".format(args_string=args_string)
            j.sal.process.execute(C, die=False)

            C = """cd {DIR_TEMP}/php && make"""
            j.sal.process.execute(C, die=False)

        # check if we need an php accelerator: https://en.wikipedia.org/wiki/List_of_PHP_accelerators

    def install(self, start=False):
        fpmdefaultconf = """\
        include={DIR_BASE}/apps/php/etc/php-fpm.d/*.conf
        """
        fpmwwwconf = """\
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
        fpmdefaultconf = textwrap.dedent(fpmdefaultconf)
        fpmwwwconf = textwrap.dedent(fpmwwwconf)
        # make sure to save that configuration file ending with .conf under php/etc/php-fpm.d/www.conf
        C = """
        cd {DIR_TEMP}/php && make install
        """

        C = j.core.tools.text_replace(C)
        j.sal.process.execute(C)
        fpmdefaultconf = j.core.tools.text_replace(fpmdefaultconf)
        fpmwwwconf = j.core.tools.text_replace(fpmwwwconf)
        j.sal.fs.writeFile("{DIR_BASE}/apps/php/etc/php-fpm.conf.default", content=fpmdefaultconf)
        j.sal.fs.writeFile("{DIR_BASE}/apps/php/etc/php-fpm.d/www.conf", content=fpmwwwconf)


        # FOR APACHE
        j.core.tools.dir_ensure('{DIR_BASE}/apps/php/lib/')
        j.builder.tools.file_copy("{DIR_TEMP}/php/php.ini-development", "{DIR_BASE}/apps/php/lib/php.ini")
        if start:
            self.start()

    def start(self):
        #TODO: needs to be redone using tmux
        phpfpmbinpath = '{DIR_BASE}/apps/php/sbin'
        # COPY BINARIES
        j.sal.process.execute("cp {DIR_BASE}/apps/php/sbin/* {DIR_BIN}")

        phpfpmcmd = "{DIR_BASE}/apps/php/sbin/php-fpm -F -y {DIR_BASE}/apps/php/etc/php-fpm.conf.default"  # foreground
        phpfpmcmd = j.core.tools.text_replace(phpfpmcmd)
        pm = j.builder.system.processmanager.get()
        pm.ensure(name="php-fpm", cmd=phpfpmcmd, path=phpfpmbinpath)

    def stop(self):
        #TODO: needs to be redone using tmux
        pm = j.builder.system.processmanager.get()
        pm.stop("php-fpm")

    def test(self):
        # TODO: *2 test php deployed in nginx
        # check there is a local nginx running, if not install it
        # deploy some php script, test it works
        raise NotImplementedError
