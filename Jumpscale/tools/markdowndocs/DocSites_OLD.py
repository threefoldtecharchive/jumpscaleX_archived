from Jumpscale import j
from .DocSite import DocSite


import imp
import time
import sys

JSBASE = j.application.JSBaseClass



class DocSites(j.application.JSBaseClass):
    """
    """

    def __init__(self):

        JSBASE.__init__(self)
        self.__imports__ = "toml"
        
        self._initOK = False
        self._macroCodepath = j.sal.fs.joinPaths(j.dirs.VARDIR, "markdowndocs_internal")
        j.sal.fs.createDir(self._macroCodepath)

        self.docsites = {}  # location in the outpath per site
        self.outpath = j.sal.fs.joinPaths(j.dirs.VARDIR, "docsite")
        self._git_repos = {}
        self.defs = {}

        self._loaded = []  # don't double load a dir
        self._configs = []  # all found config files

        self._macros = {}
        self._macros_loaded = []
        self._macros_modules = {}

        self._pointer_cache = {}  # so we don't have to full lookup all the time

        self._logger_enable()

    def _git_get(self, path):
        if path not in self._git_repos:
            try:
                gc = j.clients.git.get(path)
            except Exception as e:
                print("cannot load git:%s" % path)
                return
            self._git_repos[path] = gc
        return self._git_repos[path]

    # def _init(self):
    #     if not self._initOK:
    #         # self.install()
    #         j.clients.redis.core_get()
    #         j.sal.fs.remove(self._macroCodepath)
    #         # load the default macro's
    #         self.macros_load("https://github.com/Jumpscale/docsite/tree/master/macros")
    #         self._initOK = True


    def load(self, path="", name=""):
        if path.startswith("http"):
            path = j.clients.git.getContentPathFromURLorPath(path)
        ds = DocSite(path=path, name=name)
        self.docsites[ds.name] = ds
        return self.docsites[ds.name]

    def git_update(self):
        if self.docsites == {}:
            self.load()
        for gc in self._git_repos:
            gc.pull()

    def item_get(self, name, namespace="", die=True, first=False):
        """
        """
        key = "%s_%s" % (namespace, name)

        import pudb
        pudb.set_trace()

        # we need the cache for performance reasons
        if not key in self._pointer_cache:

            # make sure we have the most dense ascii name for search
            ext = j.sal.fs.getFileExtension(name).lower()
            name = name[:-(len(ext)+1)]  # name without extension
            name = j.core.text.strip_to_ascii_dense(name)

            namespace = j.core.text.strip_to_ascii_dense(namespace)

            if not namespace == "":
                ds = self.docsite_get(namespace)
                res = self._items_get(name, ds=ds)

                # found so will return & remember
                if len(res) == 1:
                    self._pointer_cache[key] = res[0]
                    return res

                # did not find so namespace does not count

            res = self._items_get(name=name, ext=ext)

            if (first and len(res) == 0) or not len(res) == 1:
                if die:
                    raise j.exceptions.Input(
                        message="Cannot find item with name:%s in namespace:'%s'" % (name, namespace))
                else:
                    self._pointer_cache[key] = None
            else:
                self._pointer_cache[key] = res[0]

        return self._pointer_cache[key]

    def _items_get(self, name, ext, ds=None, res=[]):
        """
        @param ds = DocSite, optional, if specified then will only look there
        """

        if ds is not None:

            if ext in ["md"]:
                find_method = ds.doc_get
            if ext in ["html", "htm"]:
                find_method = ds.html_get
            else:
                find_method = ds.file_get

            res0 = find_method(name=name+"."+ext, die=False)

            if res0 is not None:
                # we have a match, lets add to results
                res.append(res0)

        else:
            for key, ds in self.docsites.items():
                res = self._items_get(name=name, ext=ext, ds=ds, res=res)

        return res

    def def_get(self, name):
        name = j.core.text.strip_to_ascii_dense(name)
        if name not in self.defs:
            raise RuntimeError("cannot find def:%s" % name)
        return self.defs[name]

    def docsite_get(self, name, die=True):
        name = j.core.text.strip_to_ascii_dense(name)
        name = name.lower()
        if name in self.docsites:
            return self.docsites[name]
        if die:
            raise j.exceptions.Input(message="Cannot find docsite with name:%s" % name)
        else:
            return None

    def test(self):
        """
        js_shell 'j.tools.markdowndocs.test()'
        """
        url = "https://github.com/threefoldtech/jumpscale_weblibs/tree/master/docsites_examples/test/"
        ds = self.load(url, name="test")

        doc = ds.doc_get("links")

        # data comes from directories above
        assert doc.data == {'color': 'green', 'importance': 'high', 'somelist': ['a', 'b', 'c']}

        print(doc.images)

        for link in doc.links:
            print(link)

        assert str(doc.link_get(cat="image", nr=0)) == 'link:image:unsplash.jpeg'
        assert str(doc.link_get(cat="link", nr=0)) == 'link:link:https://unsplash.com/'

        doc = ds.doc_get("include_test")

        assert "## something to include" in doc.markdown
        assert "COULD NOT INCLUDE:core9:macros (not found)" in doc.markdown  # the to be included document does not exist in this test

        doc = ds.doc_get("use_data")
        md = str(doc.markdown)
        assert "- a" in md
        assert "- b" in md
        assert "high" in md

        doc = ds.doc_get("has_data")  # combines data from subdirs as well as data from doc itself

        assert doc.data == {'color': 'blue',
                            'colors': ['blue', 'red'],
                            'importance': 'somewhat',
                            'somelist': ['a', 'b', 'c']}

        print("test of docsite done")
