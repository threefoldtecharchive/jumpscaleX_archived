from Jumpscale import j
from .DocSite import DocSite
import gevent
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import imp
import time
import sys

JSBASE = j.application.JSBaseClass

class Watcher:
    """
    a class to watch all dirs loaded in the docsite and reload it once changed
    """
    def __init__(self, docsites):
        print("initializing watcher for paths: {}".format(docsites))
        event_handler = DocsiteChangeHandler()
        event_handler.register_docsites(docsites)
        event_handler.register_watcher(self)
        self.observer = PausingObserver()
        for _, docsite in docsites.items():
            self.observer.schedule(event_handler, docsite.path, recursive=True)

    def start(self):
        print("started watcher")
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class PausingObserver(Observer):
    def dispatch_events(self, *args, **kwargs):
        if not getattr(self, '_is_paused', False):
            super(PausingObserver, self).dispatch_events(*args, **kwargs)

    def pause(self):
        self._is_paused = True

    def resume(self):
        time.sleep(5)  # allow interim events to be queued
        self.event_queue.queue.clear()
        self._is_paused = False

class DocsiteChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        docsite = self.get_docsite_from_path(event.src_path)
        if docsite:
            site = j.tools.markdowndocs.load(docsite.path, docsite.name)
            self.watcher.observer.pause()
            site.write()
            self.watcher.observer.resume()

    def register_docsites(self, docsites):
        self.docsites = docsites

    def register_watcher(self, watcher):
        self.watcher = watcher

    def get_docsite_from_path(self, path):
        for _, docsite in self.docsites.items():
            if path in docsite.path:
                return docsite

class MarkDownDocs(j.application.JSBaseClass):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.markdowndocs"
        JSBASE.__init__(self)

        j.clients.redis.core_get()

        self.__imports__ = "toml"
        self._macroPathsDone = []
        self._initOK = False
        self._macroCodepath = j.sal.fs.joinPaths(
            j.dirs.VARDIR, "markdowndocs_internal", "macros.py")
        j.sal.fs.createDir(j.sal.fs.joinPaths(
            j.dirs.VARDIR, "markdowndocs_internal"))

        self.docsites = {}  # location in the outpath per site
        self.outpath = j.sal.fs.joinPaths(j.dirs.VARDIR, "markdowndocs")
        self._git_repos = {}
        self.defs = {}

        self._loaded = []  # don't double load a dir
        self._configs = []  # all found config files
        # self._macros_loaded = []

        self._macros_modules = {} #key is the path
        self._macros = {} #key is the name

        self._pointer_cache = {}  # so we don't have to full lookup all the time (for markdown docs)

        #lets make sure we have default macros
        self.macros_load()

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
    #         self.macros_load("https://github.com/Jumpscale/markdowndocs/tree/master/macros")
    #         self._initOK = True

    def macros_load(self, pathOrUrl="https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/tools/markdowndocs/macros"):
        """
        @param pathOrUrl can be existing path or url
        """
        self._logger.info("load macros:%s"%pathOrUrl)

        path = j.clients.git.getContentPathFromURLorPath(pathOrUrl)

        if path not in self._macros_modules:

            if not j.sal.fs.exists(path=path):
                raise j.exceptions.Input("Cannot find path:'%s' for macro's, does it exist?" % path)

            for path0 in j.sal.fs.listFilesInDir(path, recursive=True, filter="*.py", followSymlinks=True):
                name = j.sal.fs.getBaseName(path0)[:-3] #find name, remove .py
                self._macros[name] = j.tools.jinja2.code_python_render(obj_key=name, path=path0,reload=False, objForHash=name)
        # else:
        #     self._logger.debug("macros not loaded, already there")

    def load(self, path="", name=""):
        self.macros_load()
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

    def webserver(self, watch=True):
        url = "https://github.com/threefoldfoundation/lapis-wiki"
        server_path = j.clients.git.getContentPathFromURLorPath(url)
        url = "https://github.com/threefoldtech/jumpscale_weblibs"
        weblibs_path = j.clients.git.getContentPathFromURLorPath(url)
        j.sal.fs.symlink("{}/static".format(weblibs_path), "{}/static/weblibs".format(server_path),
                         overwriteTarget=False)
        cmd = "cd {0} && moonc . && lapis server".format(server_path)
        j.tools.tmux.execute(cmd, reset=False)

        if watch:
            watcher = Watcher(self.docsites)
            watcher.start()

    def syncer(self):
        print("syncer started, will reload every 5 mins")
        while True:
            print("Reloading")
            self.load_wikis()
            gevent.sleep(1)

    def load_wikis(self):
        url = "https://github.com/threefoldfoundation/info_tokens/tree/master/docs"
        tf_tokens = self.load(url, name="tokens")
        tf_tokens.write()

        url = "https://github.com/threefoldfoundation/info_foundation/tree/master/docs"
        tf_foundation = self.load(url, name="foundation")
        tf_foundation.write()

        url = "https://github.com/threefoldfoundation/info_grid/tree/master/docs"
        tf_grid = self.load(url, name="grid")
        tf_grid.write()

        url = "https://github.com/threefoldfoundation/info_tech/tree/master/docs"
        tf_tech = self.load(url, name="tech")
        tf_tech.write()


    def test(self):
        """
        js_shell 'j.tools.markdowndocs.test()'
        """
        url = "https://github.com/threefoldtech/jumpscale_weblibs/tree/master/docsites_examples/test/"
        ds = self.load(url, name="test")

        url = "https://github.com/threefoldtech/jumpscaleX/blob/master/docs"
        ds_js = self.load(url, name="jumpscale")

        doc = ds.doc_get("links")

        assert doc.data == {'color': 'green', 'importance': 'high', 'somelist': ['a', 'b', 'c']}

        print(doc.images)

        for link in doc.links:
            print(link)


        assert str(doc.link_get(cat="image", nr=0)) == 'link:image:unsplash.jpeg'
        assert str(doc.link_get(cat="link", nr=0)) == 'link:link:https://unsplash.com/'

        doci = ds.doc_get("include_test")

        print(doci.markdown_obj)

        print("### PROCESSED MARKDOWN DOC")

        print(doci.markdown)

        doc = ds.doc_get("use_data")
        md = str(doc.markdown)
        assert "- a" in md
        assert "- b" in md
        assert "high" in md

        doc = ds.doc_get("has_data") #combines data from subdirs as well as data from doc itself

        assert doc.data == {'color': 'blue',
                         'colors': ['blue', 'red'],
                         'importance': 'somewhat',
                         'somelist': ['a', 'b', 'c']}


        print ("test of docsite done")

        #TODO Fix Macros include for another docs in other repos i.e. include(core9:macros)
        #include of a markdown doc in a repo
        # p=doci.markdown_obj.parts[-2]
        # assert str(p).find("rivine client itself")!=-1
        #
        # #this was include test of docstring of a method
        # p=doci.markdown_obj.parts[-6]
        # assert str(p).find("j.tools.fixer.write_changes()")!=-1

        #next will rewrite the full pre-processed docsite
        ds.write()

        ds_js.write()

        url = "https://github.com/threefoldfoundation/info_tokens/tree/master/docs"
        ds4 = self.load(url, name="tf_tokens")
        ds4.write()

        url = "https://github.com/threefoldfoundation/info_foundation/tree/development/docs"
        ds5 = self.load(url, name="tf_foundation")
        ds5.write()

        url = "https://github.com/threefoldfoundation/info_grid/tree/development/docs"
        ds6= self.load(url, name="tf_grid")
        ds6.write()

        self.webserver()

        print ("TEST FOR MARKDOWN PREPROCESSING IS DONE")
