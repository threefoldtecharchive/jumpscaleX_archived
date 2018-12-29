from Jumpscale import j
from .Doc import  Doc
from .WebAsset import WebAsset

class DocSite(j.application.JSFactoryBaseClass):

    _SCHEMATEXT = """
        @url = jumpscale.docs.docsite.1
        name* = ""
        path = ""
        git_url = ""
        description = ""
        last_process_data = (D)
        """

    def _childclass_selector(self,dataobj,kwargs,childclass_name="doc"):
        """
        childclass name is webasset or doc
        :return:
        """
        if childclass_name=="doc":
            return Doc
        elif childclass_name=="webasset":
            return WebAsset
        elif childclass_name=="sidemenu":
            return SideMenu
        else:
            raise RuntimeError("did not find childclass")

    def _init(self):
        self._git = None

    @property
    def _error_file_path(self):
        if self.path is None or self.path is "":
            raise RuntimeError("path should not be empty")
        return self.path + "/errors.md"

    def get_doc(self,name=None,id=None,die=True ,create_new=True,**kwargs):
        return self.get(name=name,id=id,die=die,create_new=create_new,childclass_name="doc",**kwargs)

    def get_webasset(self,name=None,id=None,die=True ,create_new=True,**kwargs):
        return self.get(name=name,id=id,die=die,create_new=create_new,childclass_name="webasset",**kwargs)


    @property
    def git(self):
        if self._git is None:
            if self.git_url is !="":
                gitpath = self.git_url
            else:
                gitpath = j.clients.git.findGitPath(self.path,die=False)
                if not gitpath:
                    return
            self._git = j.clients.git.get(gitpath)
        return self._git

    def push_to_redis(self):
        j.shell()

    def load_from_filesystem(self,reset=False):
        """
        walk in right order over all files which we want to potentially use (include)
        and remember their paths

        if duplicate only the first found will be used

        """
        if reset == False and self._loaded:
            return

        self._files={}
        self._docs={}
        self._sidebars={}

        j.sal.fs.remove(self.path + "errors.md")
        path = self.path
        if not j.sal.fs.exists(path=path):
            raise j.exceptions.NotFound("Cannot find source path in load:'%s'" % path)

        def callbackForMatchDir(path, arg):
            base = j.sal.fs.getBaseName(path).lower()
            if base.startswith("."):
                return False
            if base.startswith("_"):
                return False
            return True

        def callbackForMatchFile(path, arg):
            base = j.sal.fs.getBaseName(path).lower()
            if base == "_sidebar.md":
                return True
            if base.startswith("_"):
                return False
            ext = j.sal.fs.getFileExtension(path)
            if ext == "md" and base[:-3] in ["summary", "default"]:
                return False
            return True

        def callbackFunctionDir(path, arg):
            # will see if ther eis data.toml or data.yaml & load in data structure in this obj
            self._processData(path + "/data")
            dpath = path + "/default.md"
            if j.sal.fs.exists(dpath, followlinks=True):
                C = j.sal.fs.readFile(dpath)
                rdirpath = j.sal.fs.pathRemoveDirPart(path, self.path)
                rdirpath = rdirpath.strip("/").strip().strip("/")
                self.content_default[rdirpath] = C
            return True

        def callbackFunctionFile(path, arg):
            self._logger.debug("file:%s"%path)
            ext = j.sal.fs.getFileExtension(path).lower()
            base = j.sal.fs.getBaseName(path)
            if ext == "md":
                self._logger.debug("found md:%s"%path)
                base = base[:-3]  # remove extension
                doc = Doc(path, base, docsite=self)
                # if base not in self.docs:
                #     self.docs[base.lower()] = doc
                self._docs[doc.name_dot_lower] = doc
            elif ext in ["html","htm"]:
                self._logger.debug("found html:%s"%path)
                # raise RuntimeError()
                # l = len(ext)+1
                # base = base[:-l]  # remove extension
                # doc = HtmlPage(path, base, docsite=self)
                # # if base not in self.htmlpages:
                # #     self.htmlpages[base.lower()] = doc
                # self.htmlpages[doc.name_dot_lower] = doc
            else:

                if ext in ["png", "jpg", "jpeg", "pdf", "docx", "doc", "xlsx", "xls", \
                            "ppt", "pptx", "mp4","css","js","mov"]:
                    self._logger.debug("found file:%s"%path)
                    base=self._clean(base)
                    if base in self._files:
                        raise j.exceptions.Input(message="duplication file in %s,%s" %  (self, path))
                    self._files[base] = path
                # else:
                #     self._logger.debug("found other:%s"%path)
                #     l = len(ext)+1
                #     base = base[:-l]  # remove extension
                #     doc = DocBase(path, base, docsite=self)
                #     if base not in self.others:
                #         self.others[base.lower()] = doc
                #     self.others[doc.name_dot_lower] = doc


        callbackFunctionDir(self.path, "")  # to make sure we use first data.yaml in root

        j.sal.fswalker.walkFunctional(
            self.path,
            callbackFunctionFile=callbackFunctionFile,
            callbackFunctionDir=callbackFunctionDir,
            arg="",
            callbackForMatchDir=callbackForMatchDir,
            callbackForMatchFile=callbackForMatchFile)

        self._loaded=True



    def error_raise(self, errormsg, doc=None):
        if doc is not None:
            errormsg2 = "## ERROR: %s\n\n- in doc: %s\n\n%s\n\n\n" % (doc.name, doc, errormsg)
            key = j.data.hash.md5_string("%s_%s"%(doc.name,errormsg))
            if not key in self._errors:
                errormsg3 = "```\n%s\n```\n"%errormsg2
                j.sal.fs.writeFile(filename=self._error_file_path, contents=errormsg3, append=True)
                self._logger.error(errormsg2)
                doc.errors.append(errormsg)
        else:
            self._logger.error("DEBUG NOW raise error")
            raise RuntimeError("stop debug here")

    @property
    def errors(self):
        """
        return current found errors
        """
        errors = "DID NOT FIND ERRORSFILE, RUN js_doc verify in the doc directory"
        if j.sal.fs.exists(self._error_file_path ):
            errors = j.sal.fs.readFile(self.error_file_path )
        return errors



    def __repr__(self):
        return "docsite:%s" % ( self.path)

    __str__ = __repr__
