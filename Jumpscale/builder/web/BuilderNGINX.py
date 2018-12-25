from Jumpscale import j
import os
import textwrap
from time import sleep





class BuilderNGINX(j.builder.system._BaseClass):
    NAME = 'nginx'

    def _init(self):
        self.BUILDDIR = j.core.tools.text_replace("{DIR_VAR}/build")

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

        	include %(DIR_VAR)s/nginx/conf/mime.types;
        	default_type application/octet-stream;

        	##
        	# SSL Settings
        	##

        	ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
        	ssl_prefer_server_ciphers on;

        	##
        	# Logging Settings
        	##

        	access_log %(DIR_VAR)s/nginx/logs/access.log;
        	error_log %(DIR_VAR)s/nginx/logs/error.log;

        	##
        	# Gzip Settings
        	##

        	gzip on;
        	gzip_disable "msie6";

        	##
        	# Virtual Host Configs
        	##

        	include %(DIR_VAR)s/nginx/conf/conf.d/*;
        	include %(DIR_VAR)s/nginx/conf/sites-enabled/*;
        }
        """ % {"DIR_VAR": self.BUILDDIR}

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
        """ % (wwwPath, self.BUILDDIR)

    def install(self, start=True):
        """
        Moving build files to build directory and copying config files
        """

        """
        # Install through ubuntu
        # j.builder.system.package.mdupdate()
        # j.builder.system.package.ensure('nginx')
        # link nginx to binDir and use it from there

        # j.core.tools.dir_ensure("{DIR_BASE}/apps/nginx/")
        # j.core.tools.dir_ensure("{DIR_BASE}/apps/nginx/bin")
        # j.core.tools.dir_ensure("{DIR_BASE}/apps/nginx/etc")
        j.core.tools.dir_ensure("{DIR_BASE}/cfg")
        j.core.tools.dir_ensure("{DIR_TEMP}")
        # j.core.tools.dir_ensure("/optvar/tmp")
        j.core.tools.dir_ensure("{DIR_BASE}/apps/nginx/")
        j.core.tools.dir_ensure("{DIR_BASE}/apps/nginx/bin")
        j.core.tools.dir_ensure("{DIR_BASE}/apps/nginx/etc")
        j.core.tools.dir_ensure("{DIR_BASE}/cfg/nginx/etc")

        j.builder.tools.file_copy('/usr/sbin/nginx', '{DIR_BASE}/apps/nginx/bin/nginx', overwrite=True)
        j.core.tools.dir_ensure('/var/log/nginx')
        j.builder.tools.file_copy('/etc/nginx/*', '{DIR_BASE}/apps/nginx/etc/', recursive=True)  # default conf
        j.builder.tools.file_copy('/etc/nginx/*', '{DIR_BASE}/cfg/nginx/etc/', recursive=True)  # variable conf
        """

        # Install nginx

        C = """
        #!/bin/bash
        set -ex

        cd {DIR_TEMP}/build/nginx/nginx-1.14.2
        make install
        """

        C = j.core.tools.text_replace(C)
        j.sal.process.execute(C)

        # Writing config files
        j.core.tools.dir_ensure("{DIR_VAR}/build/nginx/conf/conf.d/")
        j.core.tools.dir_ensure("{DIR_VAR}/build/nginx/conf/sites-enabled/")

        basicnginxconf = self.get_basic_nginx_conf()
        defaultenabledsitesconf = self.get_basic_nginx_site()

        j.sal.fs.writeFile("{DIR_VAR}/build/nginx/conf/nginx.conf", contents=basicnginxconf)
        j.sal.fs.writeFile("{DIR_VAR}/build/nginx/conf/sites-enabled/default", contents=defaultenabledsitesconf)

        fst_cgi_conf = j.core.tools.file_text_read("{DIR_VAR}/build/nginx/conf/fastcgi.conf")
        fst_cgi_conf = fst_cgi_conf.replace("include fastcgi.conf;",
                                            j.core.tools.text_replace("include {DIR_VAR}/build/nginx/conf/fastcgi.conf;"))
        j.sal.fs.writeFile("{DIR_VAR}/build/nginx/conf/fastcgi.conf", contents=fst_cgi_conf)

        #j.builder.tools.file_link(source="{DIR_BASE}/cfg/nginx", destination="{DIR_BASE}/apps/nginx")
        if start:
            self.start()

    def build(self, install=True):
        """ Builds NGINX server
        Arguments:
            install {[bool]} -- [If True, the server will be installed locally after building](default: {True})
        """
        j.tools.bash.local.locale_check()

        if j.core.platformtype.myplatform.isUbuntu:
            j.sal.ubuntu.apt_update()
            j.sal.ubuntu.apt_install(
                "build-essential libpcre3-dev libssl-dev zlibc zlib1g zlib1g-dev", update_md=False)
            
            tmp_dir = j.core.tools.text_replace("{DIR_TEMP}/build/nginx")
            j.core.tools.dir_ensure(tmp_dir, remove_existing=True)
            build_dir = j.core.tools.text_replace("{DIR_VAR}/build/nginx")
            j.core.tools.dir_ensure(tmp_dir, remove_existing=True)

            C = """
            #!/bin/bash
            set -ex

            cd {DIR_TEMP}/build/nginx
            wget https://nginx.org/download/nginx-1.14.2.tar.gz
            tar xzf nginx-1.14.2.tar.gz

            cd nginx-1.14.2
            ./configure --prefix={DIR_VAR}/build/nginx/ --with-http_ssl_module --with-ipv6
            make
            """
            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)

        else:
            raise j.exceptions.NotImplemented(message="only ubuntu supported for building nginx")

        if install:
            self.install()

    def start(self, nodaemon=True, nginxconfpath=None):
        nginxbinpath = '{DIR_VAR}/build/nginx/sbin'
        # COPY BINARIES TO BINDIR
        j.core.tools.dir_ensure('{DIR_BIN}')
        cmd = j.core.tools.text_replace(
            "cp {DIR_VAR}/build/nginx/sbin/* {DIR_BIN}/")
        j.sal.process.execute(cmd)

        if nginxconfpath is None:
            nginxconfpath = '{DIR_VAR}/build/nginx/conf/nginx.conf'

        nginxconfpath = j.core.tools.text_replace(nginxconfpath)
        nginxconfpath = os.path.normpath(nginxconfpath)

        if j.sal.fs.exists(nginxconfpath):
            # foreground
            nginxcmd = "%s/nginx -c %s -g 'daemon off;'" % (nginxbinpath, nginxconfpath)
            nginxcmd = j.core.tools.text_replace(nginxcmd)

            self._logger.info("cmd: %s" % nginxcmd)
            j.tools.tmux.execute(nginxcmd, window=self.NAME,
                                 pane=self.NAME, reset=True)

        else:
            raise RuntimeError('Failed to start nginx')

    def stop(self):
        j.sal.process.killProcessByName(self.NAME)
        

    def test(self):
        # host a file test can be reached
        raise NotImplementedError
