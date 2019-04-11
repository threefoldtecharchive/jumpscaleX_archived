from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass


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

    @staticmethod
    def generate_docsite(name, repo_url):
        url = "{}/tree/{}/docs".format(repo_url, "master")
        doc_site = j.tools.markdowndocs.load(url, name=name)
        doc_site.write()

        dev_dest = j.clients.git.getGitRepoArgs(repo_url)[-3] + "-dev"
        j.clients.git.pullGitRepo(repo_url, branch="development", dest=dev_dest)
        docs_path = "{}/docs".format(dev_dest)
        doc_site = j.tools.markdowndocs.load(docs_path, name=name + "-dev")
        doc_site.write()

    def add_wiki(self, name, repo_url, domain):
        # Generate md files for master and dev branches
        self.generate_docsite(name, repo_url)

        # Generate nginx config file for wiki

        wiki = self.wikis.new()
        wiki.name = name
        wiki.repo_url = repo_url
        wiki.domain = domain
