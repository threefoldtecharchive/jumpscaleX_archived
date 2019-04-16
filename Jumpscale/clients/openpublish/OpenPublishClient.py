import os
import gevent
from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass
MASTER_BRANCH = "master"
DEV_BRANCH = "development"
DEV_SUFFIX = "_dev"
CONFIG_TEMPLATE = "CONF_TEMPLATE"


class OpenPublishClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.open_publish.1
        name* = "" (S)
        websites = (LO) !jumpscale.open_publish.website.1
        wikis = (LO) !jumpscale.open_publish.wiki.1
            
        @url = jumpscale.open_publish.website.1
        name = "" (S)
        repo_url = "" (S)
        domain = "" (S)
        
        @url = jumpscale.open_publish.wiki.1
        name = "" (S)
        repo_url = "" (S)
        domain = "" (S)
    """

    def _init(self):
        open_publish_repo = "https://github.com/threefoldfoundation/lapis-wiki"
        self.open_publish_path = j.clients.git.getContentPathFromURLorPath(open_publish_repo)

    def auto_update(self):
        while True:
            for wiki in self.wikis:
                self._log_info("Updating: {}".format(wiki.name))
                self.load_site(wiki, MASTER_BRANCH)
                self.load_site(wiki, DEV_BRANCH, DEV_SUFFIX)
            print("Reloading docsites")
            gevent.sleep(300)

    def server_start(self):
        url = "https://github.com/threefoldtech/jumpscale_weblibs"
        weblibs_path = j.clients.git.getContentPathFromURLorPath(url)
        j.sal.fs.symlink("{}/static".format(weblibs_path), "{}/static/weblibs".format(self.open_publish_path),
                         overwriteTarget=False)
        cmd = "cd {0} && moonc . && lapis server".format(self.open_publish_path)
        j.tools.tmux.execute(cmd, reset=False, window="web_server")

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
        self.reload_server()

    def add_wiki(self, name, repo_url, domain):
        wiki = self.wikis.new(data=dict(name=name, repo_url=repo_url, domain=domain))

        # Generate md files for master and dev branches
        self.load_site(wiki, MASTER_BRANCH)
        self.load_site(wiki, DEV_BRANCH, DEV_SUFFIX)

        # Generate nginx config file for wiki
        self.generate_nginx_conf(wiki)
        self.save()

    def add_website(self, name, repo_url, domain):
        website = self.websites.new(name=name, repo_url=repo_url, domain=domain)

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
