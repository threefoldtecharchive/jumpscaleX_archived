from Jumpscale import j
import os
import textwrap
from time import sleep

builder_method = j.builder.system.builder_method
class BuilderNGINX(j.builder.system._BaseClass):
    NAME = 'nginx'

    def get_basic_nginx_conf(self):
        return """\
        user www-data;
        worker_processes auto;
        pid /run/nginx.pid;

        events {
        	worker_connections 768;
        	# multi_accept on;
        }

        http {

        	##
        	# Basic Settings
        	##

        	sendfile on;
        	tcp_nopush on;
        	tcp_nodelay on;
        	keepalive_timeout 65;
        	types_hash_max_size 2048;
        	# server_tokens off;

        	# server_names_hash_bucket_size 64;
        	# server_name_in_redirect off;

        	include %(DIR_APPS)s/conf/mime.types;
        	default_type application/octet-stream;

        	##
        	# SSL Settings
        	##

        	ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
        	ssl_prefer_server_ciphers on;

        	##
        	# Logging Settings
        	##

        	access_log %(DIR_APPS)s/logs/access.log;
        	error_log %(DIR_APPS)s/logs/error.log;

        	##
        	# Gzip Settings
        	##

        	gzip on;
        	gzip_disable "msie6";

        	##
        	# Virtual Host Configs
        	##

        	include %(DIR_APPS)s/conf/conf.d/*;
        	include %(DIR_APPS)s/conf/sites-enabled/*;
        }
        """ % {"DIR_APPS": self.DIR_BUILD}

    def get_basic_nginx_site(self, wwwPath="/var/www/html"):
        return """\
        server {
            listen 80 default_server;
            listen [::]:80 default_server;

            root %s;

            # Add index.php to the list if you are using PHP
            index index.html index.htm index.nginx-debian.html index.php;

            server_name _;

            location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
            }

            # location ~ \.php$ {
                # include %s/nginx/conf/snippets/fastcgi-php.conf;

                # With php7.0-cgi alone:
                # fastcgi_pass 127.0.0.1:9000;
            # With php7.0-fpm:
                # fastcgi_pass unix:/run/php/php7.0-fpm.sock;
            # }
        }
        """ % (wwwPath, self.DIR_BUILD)

    @builder_method()
    def install(self, tmux=True):
        """
        Moving build files to build directory and copying config files
        """
        # Install nginx

        C = """
        #!/bin/bash
        set -ex

        cd {DIR_TEMP}/build/nginx/nginx-1.14.2
        make install
        """
        self._execute(C)

        # COPY BINARIES TO BINDIR
        self.tools.dir_ensure('{DIR_BIN}')
        cmd = self._replace(
            "cp {DIR_BUILD}/sbin/* {DIR_BIN}/")
        self._execute(cmd)

        # Writing config files
        self.tools.dir_ensure("{DIR_BUILD}/conf/conf.d/")
        self.tools.dir_ensure("{DIR_BUILD}/conf/sites-enabled/")

        basicnginxconf = self.get_basic_nginx_conf()
        defaultenabledsitesconf = self.get_basic_nginx_site()
        self.tools.file_write("{DIR_BUILD}/conf/nginx.conf", content=basicnginxconf)
        self.tools.file_write("{DIR_BUILD}/conf/sites-enabled/default", content=defaultenabledsitesconf)

        fst_cgi_conf = self._read("{DIR_BUILD}/conf/fastcgi.conf")
        fst_cgi_conf = fst_cgi_conf.replace("include fastcgi.conf;",
                                            self._replace("include {DIR_BUILD}/conf/fastcgi.conf;"))
        self.tools.file_write("{DIR_BUILD}/conf/fastcgi.conf", content=fst_cgi_conf)


    @builder_method()
    def build(self, reset=False):
        """ Builds NGINX server
        Arguments:
            install {[bool]} -- [If True, the server will be installed locally after building](default: {True})
        """
        j.tools.bash.get().profile.locale_check()

        if self.tools.isUbuntu:
            self.system.package.mdupdate()
            self.system.package.install(["build-essential", "libpcre3-dev", "libssl-dev", "zlibc", "zlib1g", "zlib1g-dev"])

            tmp_dir = self._replace("{DIR_TEMP}/build/nginx")
            self.tools.dir_ensure(tmp_dir)
            build_dir = self._replace("{DIR_BUILD}")
            self.tools.dir_ensure(build_dir)

            C = """
            #!/bin/bash
            set -ex

            cd {DIR_TEMP}/build/nginx
            wget https://nginx.org/download/nginx-1.14.2.tar.gz
            tar xzf nginx-1.14.2.tar.gz

            cd nginx-1.14.2
            ./configure --prefix={DIR_BUILD} --with-http_ssl_module --with-ipv6
            make
            """
            self._replace(C)
            self._execute(C, showout=False)

        else:
            raise j.exceptions.NotImplemented(message="only ubuntu supported for building nginx")


    @property
    def startup_cmds(self,nginxconfpath=None):
        if nginxconfpath is None:
            nginxconfpath = '{DIR_APPS}/nginx/conf/nginx.conf'

        nginxconfpath = self._replace(nginxconfpath)
        nginxconfpath = os.path.normpath(nginxconfpath)        

        if self.tools.file_exists(nginxconfpath):
            # foreground
            nginxcmd = "%s -c %s -g 'daemon off;'" % (self.NAME, nginxconfpath)
            nginxcmd = self._replace(nginxcmd)

            self._log_info("cmd: %s" % nginxcmd)
            # j.tools.tmux.execute(nginxcmd, window=self.NAME,
            #                      pane=self.NAME, reset=True)
            cmd = j.tools.startupcmd.get("nginx", cmd=nginxcmd, path="/sandbox/bin")
            return [cmd]
        else:
            raise RuntimeError('Failed to start nginx')

    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        # test is already implemented in php runtime
        pass

    def sandbox(self, dest_path='/tmp/builder/nginx', create_flist=True, zhub_instance=None, reset=False):
        '''Copy built bins to dest_path and create flist if create_flist = True
            :param dest_path: destination path to copy files into
            :type dest_path: str
            :param sandbox_dir: path to sandbox
            :type sandbox_dir: str
            :param reset: reset sandbox file transfer
            :type reset: bool
            :param create_flist: create flist after copying files
            :type create_flist:bool
            :param zhub_instance: hub instance to upload flist to
            :type zhub_instance:str
        '''
        if self._done_check('sandbox') and not reset:
            return
        self.build(reset=reset)

        dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, self.NAME)
        dir_dest = j.sal.fs.joinPaths(dest_path, j.core.dirs.BINDIR[1:])
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyFile(dir_src, dir_dest)
        confs = {'{DIR_APPS}/nginx/conf/fastcgi.conf': '/sandbox/{DIR_APPS}/nginx/conf/fastcgi.conf',
                 '{DIR_APPS}/nginx/conf/nginx.conf': '/sandbox/nginx/conf/nginx.conf'}

        self.copy_dirs(dirs=confs, dest=dest_path)

        self._done_set('sandbox')
        if create_flist:
            self.flist_create(dest_path, zhub_instance)
