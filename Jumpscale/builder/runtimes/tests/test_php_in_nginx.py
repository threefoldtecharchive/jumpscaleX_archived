import pytest
import os
import requests
import time

from Jumpscale import j


def get_test_nginx_site(www_path="/var/www/html"):
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

        location ~* \.php$ {
            fastcgi_index   index.php;
            fastcgi_pass    127.0.0.1:9000;
            include         fastcgi_params;
            fastcgi_param   SCRIPT_FILENAME    $document_root$fastcgi_script_name;
            fastcgi_param   SCRIPT_NAME        $fastcgi_script_name;
        }
    }
    """ % www_path


@pytest.mark.integration
def test_main(self=None):
    """
    to run:

    js_shell 'j.builders.runtime.php._test(name="php_in_nginx")'

    """
    # check if nginx is installed, if not then install it
    if not j.sal.process.checkInstalled(j.builder.web.nginx.NAME):
        j.builder.web.nginx.build(install=True)
    # check if php is installed, if not then install it
    if not j.sal.process.checkInstalled(j.builder.runtimes.php.NAME):
        j.builder.runtimes.php.build(install=True)
    try:
        www_path = self._replace(
            "{DIR_TEMP}/www/html"
        )
        j.core.tools.dir_ensure(www_path)
        default_enabled_sites_conf = get_test_nginx_site(www_path)
        default_site_path = self._replace(
            "{DIR_APPS}/nginx/conf/sites-enabled/default")
        default_site_backup_path = self._replace("{DIR_TEMP}/default_nginx_site.bak")
        j.sal.fs.moveFile(default_site_path, default_site_backup_path)
        j.sal.fs.writeFile(default_site_path, contents=default_enabled_sites_conf)
        j.sal.fs.writeFile(j.sal.fs.joinPaths(www_path, 'index.php'),
                           contents="<?php phpinfo(); ?>"
        )
        j.builder.runtimes.php.start()
        j.builder.web.nginx.stop()
        j.builder.web.nginx.start()
        
        # wait until port is ready
        time.sleep(30)

        # test executing the php index file
        res = requests.get("http://localhost")
        assert res.status_code == 200, "Failed to retrieve deployed php page. Error: {}".format(res.text)

    finally:
        j.sal.fs.remove(os.path.dirname(www_path))
        if j.sal.fs.exists(default_site_backup_path):
            j.sal.fs.moveFile(default_site_backup_path, default_site_path)
        j.builder.web.nginx.stop()
        j.builder.web.nginx.start()
        j.builder.runtimes.php.start()
