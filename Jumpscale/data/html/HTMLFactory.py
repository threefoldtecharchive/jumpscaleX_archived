from Jumpscale import j

JSBASE = j.application.JSBaseClass
from importlib import import_module
from inspect import isfunction
import sys
from .HTMLPage import HTMLPage
from .HTMLWebParts import HTMLWebParts
from html2text import HTML2Text

class HTMLFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.html"
        JSBASE.__init__(self)
        self.webparts = HTMLWebParts()
        self._webparts_done = []

    def html2text(self, html):
        """
        """
        html = str(html, errors='ignore')
        encoding = "utf-8"
        html = html.decode(encoding)
        h = HTML2Text()

        # # handle options
        # if options.ul_style_dash: h.ul_item_mark = '-'
        # if options.em_style_asterisk:
        #     h.emphasis_mark = '*'
        #     h.strong_mark = '__'

        h.body_width = 0
        # h.list_indent = options.list_indent
        # h.ignore_emphasis = options.ignore_emphasis
        # h.ignore_links = options.ignore_links
        # h.ignore_images = options.ignore_images
        # h.google_doc = options.google_doc
        # h.hide_strikethrough = options.hide_strikethrough
        # h.escape_snob = options.escape_snob

        text = h.handle(html)
        text.encode('utf-8')

        return text


    def page_get(self):
        """
        return a html page on which content can be dynamically build

        """
        return HTMLPage()

    def webparts_enable(self,url=""):
        """
        will load webparts from https://github.com/threefoldtech/jumpscale_weblibs/tree/master/webparts if not url defined

        each webpart is an add function to manipulate the html page object

        """
        if not url:
            url = "https://github.com/threefoldtech/jumpscale_weblibs/tree/master/webparts"
        if url in self._webparts_done:
            return
        path = j.clients.git.getContentPathFromURLorPath(url)
        if path not in sys.path:
            sys.path.append(path)
        for webpart_name in  j.sal.fs.listDirsInDir(path,False,True):
            self._logger.info("found webpart:%s"%webpart_name)
            path2="%s/%s/add.py"%(path,webpart_name)
            if not j.sal.fs.exists(path2):
                raise RuntimeError("cannot find webpart:%s"%path2)
            module = import_module("%s.add"%webpart_name)
            self.webparts.modules[webpart_name]=module
            for key,item in module.__dict__.items():
                if isfunction(item):
                    if (key.find("_add") is not -1 or key is "add") and not key.startswith("_"):
                        self.webparts.__dict__["%s_%s"%(webpart_name,key)]=item
            
        if j.servers.web.latest is not None:
            j.servers.web.latest.webparts = self.webparts

        self._webparts_done.append(url)

    # def register_blueprints(self,app):
    #     apps = j.sal.fs.listDirsInDir("%s/blueprints"%self.path, recursive=False, dirNameOnly=True, findDirectorySymlinks=True, followSymlinks=True)
    #     apps = [item for item in apps if item[0] is not "_"]
    #     for module_name in apps:
    #         module = import_module('blueprints.{}.routes'.format(module_name))
    #         print("blueprint register:%s"%module_name)
    #         app.register_blueprint(module.blueprint)        

    def test(self):
        """
        js_shell 'j.data.html.test()'
        """

        p = j.data.html.page_get()
        p.header_add("this is my heading")

        list=["aa","bb","cc"]
        p.list_add(list)

        p.newline_add()

        p.listitem_add("something 1", level=1)
        p.listitem_add("something 2", level=2)
        p.listitem_add("something 3", level=3)
        p.listitem_add("something 4", level=2)
        p.listitem_add("something 5", level=2)
        p.listitem_add("something 6", level=3)
        # p.listitem_add("something 7", level=1)

        print(p)


