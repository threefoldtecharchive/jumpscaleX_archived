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
compileconfig['prefix'] = "{DIR_APPS}/php"
compileconfig['exec_prefix'] = "{DIR_APPS}/php"
compileconfig['with_mysqli'] = True
compileconfig['with_pdo_mysql'] = True
compileconfig['with_mysql_sock'] = "/var/run/mysqld/mysqld.sock"


class BuilderPHP(j.builder.system._BaseClass):

    NAME = 'php-fpm'

    def build(self, install=False, **config):
        '''
        js_shell 'j.builder.runtimes.php.build()'
        :param config:
        :return:
        '''
        j.tools.bash.get().locale_check()

        if j.core.platformtype.myplatform.isUbuntu:
            pkgs = "libxml2-dev libpng-dev libcurl4-openssl-dev libzip-dev zlibc zlib1g zlib1g-dev \
            libmysqld-dev libmysqlclient-dev re2c bison bzip2 build-essential libaprutil1-dev libapr1-dev \
            openssl pkg-config libssl-dev file"
            j.sal.ubuntu.apt_update()
            j.sal.ubuntu.apt_install(pkgs, update_md=False)
            
            C = """
            set -x
            rm -f {DIR_TEMP}/php-7.3.0.tar.bz*
            cd {DIR_TEMP} && [ ! -f {DIR_TEMP}/php-7.3.0.tar.bz2 ] && wget http://be2.php.net/distributions/php-7.3.0.tar.bz2
            cd {DIR_TEMP} && tar xvjf {DIR_TEMP}/php-7.3.0.tar.bz2
            mv {DIR_TEMP}/php-7.3.0/ {DIR_TEMP}/php
            """

            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)

            compileconfig['with_apxs2'] = j.core.tools.text_replace("{DIR_APPS}/apache2/bin/apxs")
            buildconfig = deepcopy(compileconfig)
            buildconfig.update(config)  # should be defaultconfig.update(config) instead of overriding the explicit ones.

            # check for apxs2 binary if it's valid.
            apxs = buildconfig['with_apxs2']
            if not j.core.tools.exists(apxs):
                buildconfig.pop('with_apxs2')

            args_string = ""
            for k, v in buildconfig.items():
                k = k.replace("_", "-")
                if v is True:
                    args_string += " --{k}".format(k=k)
                else:
                    args_string += " --{k}={v}".format(k=k, v=v)
            args_string = j.core.tools.text_replace(args_string)
            C = """cd {DIR_TEMP}/php && ./configure %s""" % args_string
            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)

            C = """cd {DIR_TEMP}/php && make"""
            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)
        else:
            raise j.exceptions.NotImplemented(
                message="only ubuntu supported for building php")
        if install is True:
            self.install()
        # check if we need an php accelerator: https://en.wikipedia.org/wiki/List_of_PHP_accelerators

    def install(self, start=False):
        fpmdefaultconf = """\
        include={DIR_APPS}/php/etc/php-fpm.d/*.conf
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

        j.core.tools.dir_ensure(j.core.tools.text_replace(
            "{DIR_APPS}/php/etc/php-fpm.d"))
        
        fpmdefaultconf = j.core.tools.text_replace(fpmdefaultconf)
        fpmwwwconf = j.core.tools.text_replace(fpmwwwconf)
        j.sal.fs.writeFile("{DIR_APPS}/php/etc/php-fpm.conf", contents=fpmdefaultconf)
        j.sal.fs.writeFile("{DIR_APPS}/php/etc/php-fpm.d/www.conf", contents=fpmwwwconf)

        php_tmp_path = j.core.tools.text_replace("{DIR_TEMP}/php")
        php_app_path = j.core.tools.text_replace("{DIR_APPS}/php")
        j.sal.fs.copyFile(j.sal.fs.joinPaths(
            php_tmp_path, 'php.ini-development'),
            j.sal.fs.joinPaths(php_app_path, 'php.ini'))
        
        # It is important that we prevent Nginx from passing requests to the PHP-FPM backend if the file does not exists, 
        # allowing us to prevent arbitrarily script injection. 
        # We can fix this by setting the cgi.fix_pathinfo directive to 0 within our php.ini file.
        C = """
        sed -i 's/;cgi.fix_pathinfo=1/;cgi.fix_pathinfo=0/g' {php_app_path}/php.ini
        """.format(php_app_path=php_app_path)
        j.sal.process.execute(C)
        
        # copy binaries
        C = """
        set +x
        cp {DIR_APPS}/php/bin/* {DIR_BIN}
        cp {DIR_APPS}/php/sbin/* {DIR_BIN}
        """
        C = j.core.tools.text_replace(C)
        j.sal.process.execute(C)
        
        if start:
            self.start()

    def start(self):
        phpfpmcmd = "%s -F -y {DIR_APPS}/php/etc/php-fpm.conf" % self.NAME  # foreground
        phpfpmcmd = j.core.tools.text_replace(phpfpmcmd)
        j.tools.tmux.execute(phpfpmcmd, window=self.NAME, pane=self.NAME, reset=True)
        

    def stop(self):
        j.sal.process.killProcessByName(self.NAME)

    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key='test_main')
