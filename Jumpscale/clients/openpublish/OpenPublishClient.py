import os
import gevent
from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass
MASTER_BRANCH = "master"
DEV_BRANCH = "development"
DEV_SUFFIX = "_dev"
CONFIG_TEMPLATE = "CONF_TEMPLATE"
OPEN_PUBLISH_REPO = "https://github.com/threefoldfoundation/lapis-wiki"


class OpenPublishClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.open_publish.1
        name* = "" (S)
        websites = (LO) !jumpscale.open_publish.website.1
        wikis = (LO) !jumpscale.open_publish.wiki.1
        gedis_port = 8888 (I)
        zdb_port = 9901 (I)
            
        @url = jumpscale.open_publish.website.1
        name = "" (S)
        repo_url = "" (S)
        domain = "" (S)
        ip = "" (ipaddr)
        
        @url = jumpscale.open_publish.wiki.1
        name = "" (S)
        repo_url = "" (S)
        domain = "" (S)
        ip = "" (ipaddr)
    """

    def _init(self):
        self.open_publish_path = j.clients.git.getContentPathFromURLorPath(OPEN_PUBLISH_REPO)
        self.gedis_server = None
        self.dns_server = None

    def auto_update(self):
        while True:
            for wiki in self.wikis:
                self._log_info("Updating: {}".format(wiki.name))
                self.load_site(wiki, MASTER_BRANCH)
                self.load_site(wiki, DEV_BRANCH, DEV_SUFFIX)
            print("Reloading docsites")
            gevent.sleep(300)

    def servers_start(self):
        # TODO Move lapis to a seperate server and just call it from here
        url = "https://github.com/threefoldtech/jumpscale_weblibs"
        weblibs_path = j.clients.git.getContentPathFromURLorPath(url)
        j.sal.fs.symlink("{}/static".format(weblibs_path), "{}/static/weblibs".format(self.open_publish_path),
                         overwriteTarget=False)

        # Start Lapis Server
        self._log_info("Starting Lapis Server")
        cmd = "moonc . && lapis server".format(self.open_publish_path)
        j.tools.startupcmd.get(name="Lapis", cmd=cmd, path=self.open_publish_path).start()

        # Start ZDB Server and create dns namespace
        self._log_info("Starting ZDB Server")
        j.servers.zdb.configure(port=self.zdb_port)
        j.servers.zdb.start()
        zdb_admin_client = j.clients.zdb.client_admin_get(port=self.zdb_port)
        zdb_std_client = zdb_admin_client.namespace_new("dns")

        # Start bcdb server and create corresponding dns namespace
        self._log_info("Starting BCDB Server")
        bcdb_name = "dns"
        j.data.bcdb.redis_server_start(name=bcdb_name, zdbclient_port=self.zdb_port,
                                       background=True, zdbclient_namespace="dns")
        bcdb = j.data.bcdb.new(bcdb_name, zdb_std_client)

        # Start DNS Server
        self.dns_server = j.servers.dns.get(bcdb=bcdb)
        gevent.spawn(self.dns_server.serve_forever)

        # Start Gedis Server
        self._log_info("Starting Gedis Server")
        self.gedis_server = j.servers.gedis.configure(host="0.0.0.0", port=self.gedis_port)
        actor_path = j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), "actors", "open_publish.py")
        self.gedis_server.actor_add(actor_path)
        self.gedis_server.start()

    def load_site(self, obj, branch, suffix=""):
        dest = j.clients.git.getGitRepoArgs(obj.repo_url)[-3] + suffix
        j.clients.git.pullGitRepo(obj.repo_url, branch=branch, dest=dest)
        docs_path = "{}/docs".format(dest)
        try:
            doc_site = j.tools.markdowndocs.load(docs_path, name=obj.name + suffix)
            doc_site.write()
        except Exception as e:
            self._log_error(e)

    def reload_server(self):
        cmd = "cd {0} && lapis build".format(self.open_publish_path)
        j.tools.executorLocal.execute(cmd)

    def generate_nginx_conf(self, obj, app="wiki"):
        if "website" in obj._schema.key:
            app = obj.name

        path = j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), CONFIG_TEMPLATE)
        dest = j.sal.fs.joinPaths(self.open_publish_path, 'vhosts', '{}.conf'.format(obj.domain))
        args = {
            'name': obj.name,
            'domain': obj.domain,
            'app': app
        }
        j.tools.jinja2.file_render(path=path, dest=dest, **args)
        self.dns_server.resolver.create_item(domain=obj.domain, value=obj.ip)
        self.reload_server()

    def add_wiki(self, name, repo_url, domain, ip):
        wiki = self.wikis.new(data=dict(name=name, repo_url=repo_url, domain=domain, ip=ip))

        # Generate md files for master and dev branches
        self.load_site(wiki, MASTER_BRANCH)
        self.load_site(wiki, DEV_BRANCH, DEV_SUFFIX)

        # Generate nginx config file for wiki
        self.generate_nginx_conf(wiki)
        self.save()

    def add_website(self, name, repo_url, domain, ip):
        website = self.websites.new(data=dict(name=name, repo_url=repo_url, domain=domain, ip=ip))

        # Generate md files for master and dev branches
        for branch in [DEV_BRANCH and MASTER_BRANCH]:
            suffix = DEV_SUFFIX if branch == DEV_BRANCH else ""
            self.load_site(website, branch, suffix)

        # Generate nginx config file for website
        self.generate_nginx_conf(website)

        # link website files into open publish dir
        src = j.sal.fs.joinPaths(j.clients.git.getGitRepoArgs(repo_url)[-3], "lapis")
        # TODO LINK static/views/moon files

        self.save()

    def remove_wiki(self, name):
        for wiki in self.wikis:
            if name == wiki.name:
                dest = j.clients.git.getGitRepoArgs(wiki.repo_url)[-3]
                j.sal.fs.remove(dest)
                j.sal.fs.remove(dest + DEV_SUFFIX)
                j.sal.fs.remove(j.sal.fs.joinPaths(j.dirs.VARDIR, "docsites", wiki.name))
                j.sal.fs.remove(j.sal.fs.joinPaths(j.dirs.VARDIR, "docsites", wiki.name + DEV_SUFFIX))
                j.sal.fs.remove(j.sal.fs.joinPaths(self.open_publish_path, 'vhosts', '{}.conf'.format(wiki.domain)))
                self.wikis.remove(wiki)
                self.save()
                self.reload_server()
                break
        else:
            raise ValueError("No wiki found with this name: {}".format(name))

    def remove_website(self, name):
        for website in self.websites:
            if name == website.name:
                dest = j.clients.git.getGitRepoArgs(website.repo_url)[-3]
                j.sal.fs.remove(dest)
                j.sal.fs.remove(dest + DEV_SUFFIX)
                try:
                    j.sal.fs.remove(j.sal.fs.joinPaths(j.dirs.VARDIR, "docsites", website.name))
                    j.sal.fs.remove(j.sal.fs.joinPaths(j.dirs.VARDIR, "docsites", website.name + DEV_SUFFIX))
                except ValueError:
                    self._log_warn("This website doesn't contain docsite to remove")
                j.sal.fs.remove(j.sal.fs.joinPaths(self.open_publish_path, 'vhosts', '{}.conf'.format(website.domain)))
                self.websites.remove(website)
                self.save()
                self.reload_server()
                break
        else:
            raise ValueError("No wiki found with this name: {}".format(name))
