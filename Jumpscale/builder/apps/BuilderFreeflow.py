from Jumpscale import j
import textwrap


class BuilderFreeflow(j.builder.system._BaseClass):
    NAME = "freeflow"

    def _init(self):

        self.HUMHUB_PATH = "/var/www/html/humhub"
        self.dirs = {
            "/var/www/html/humhub": "/var/www/html/humhub",
            "/var/lib/mysql/": "/var/lib/mysql/",
            "/var/log/mysql/": "/var/log/mysql/",
            "/var/run/mysqld/": "/var/run/mysqld/",
            "/etc/apache2": "/etc/apache2"

        }
        self.dirs.update(j.builder.db.mariadb.dirs)

        self.bins = [
            "/usr/bin/mysql",
            "/usr/sbin/apache2"
        ]
        self.bins.extend(j.builder.db.mariadb.bins)

        self.new_files = {"//.startup.toml": self.startup_script}
        self.new_files.update(j.builder.db.mariadb.new_files)


    def build(self):

        j.builder.db.mariadb.install(start=True)
        j.builder.system.package.install(["apache2",
                                         "php-curl",
                                         "php-gd",
                                         "php-mbstring",
                                         "php-intl",
                                         "php-zip",
                                         "php-ldap",
                                         "php-apcu"
                                         ])

        j.builder.tools.file_download("https://www.humhub.org/en/download/package/humhub-1.3.7.tar.gz",
                                      "/var/www/html/humhub-1.3.7.tar.gz")
        j.builder.tools.file_expand("/var/www/html/humhub-1.3.7.tar.gz", self.HUMHUB_PATH, removeTopDir=True)





        sql_init_script = """
        mysql -e "CREATE DATABASE humhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        mysql -e "GRANT ALL ON humhub.* TO 'humhub'@'localhost' IDENTIFIED BY 'Hum_flist_hubB';"
        mysql -e "FLUSH PRIVILEGES;"
        """
        j.builder.tools.run(sql_init_script)

        j.builder.tools.file_download("https://raw.githubusercontent.com/threefoldgrid/freeflow/master/utils/IYO.php",
                                      "/var/www/html/humhub/protected/humhub/modules/user/authclient/IYO.php")

        j.builder.tools.file_download("https://raw.githubusercontent.com/threefoldgrid/freeflow/master/utils/common.php",
                                      "/var/www/html/humhub/protected/config/common.php")

        j.sal.fs.chmod("/var/www", 0o775)

        j.sal.fs.chown("/var/www", "www-data", "www-data")


    @property
    def startup_script(self):
        return """
[startup.mysql]
name = "core.system"
after = ["setup"]
protected = true

[startup.mysql.args]
name = "mysqld"

[startup.apache]
name = "core.system"
protected = true
after = ["setup"]

[startup.apache.args]
name = "apachectl"
args = [
    "-DFOREGROUND"
]

[startup.cron1]
name = "bash"
recurring_period = 60

[startup.cron1.args]
script = \"""
/usr/bin/php /var/www/html/humhub/protected/yii queue/run >/dev/null 2>&
\"""

[startup.cron2]
name = "bash"
recurring_period=60

[startup.cron2.args]
script = \"""
/usr/bin/php /var/www/html/humhub/protected/yii cron/run >/dev/null 2>&1
\"""

[startup.setup]
name = "bash"
running_delay = -1

[startup.setup.args]
script = \"""
sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
export HOME=/root
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
chmod -R 775 /var/www/

chmod 400 -R /etc/ssh/
chown -R www-data:www-data /var/www/

chown -R mysql /var/lib/mysql/
chown -R mysql /var/log/mysql/
chown -R mysql /var/run/mysqld/
\"""
        """