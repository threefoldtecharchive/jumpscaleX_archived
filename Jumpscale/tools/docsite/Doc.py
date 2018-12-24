from Jumpscale import j
import toml

import copy

JSBASE = j.application.JSBaseClass
from .Link import Link
from urllib.parse import urlparse,parse_qs,parse_qsl

class Doc(j.builder._BaseClass):
    """
    """

    def __init__(self, path, name, docsite):
        JSBASE.__init__(self)
        self.path = path
        self.docsite = docsite

        self.cat = ""
        if "/blogs/" in path or "/blog/" in path:
            self.cat = "blog"
        if "/defs/" in path or "/def/" in path:
            self.cat = "def"            
        
        self.path_dir = j.sal.fs.getDirName(self.path)
        self.path_dir_rel = j.sal.fs.pathRemoveDirPart(self.path_dir, self.docsite.path).strip("/")
        self.name = self._clean(name)
        if self.name == "":
            raise RuntimeError("name cannot be empty")
        self.name_original = name
        self.path_rel = j.sal.fs.pathRemoveDirPart(path, self.docsite.path).strip("/")

        name_dot =  "%s/%s" % (self.path_dir_rel,self.name)
        self.name_dot_lower = self._clean("%s/%s" % (self.path_dir_rel,self.name))

        # self.markdown_source = ""
        # self.show = True
        self.errors = []

        if j.sal.fs.getDirName(self.path).strip("/").split("/")[-1][0] == "_":
            # means the subdir starts with _
            self.show = False

        self._processed = False

        self._extension = None

        self._data = {} #is all data, from parents as well, also from default data

        self._md = None

        self._content = None

        self._images = []
        self._links_external = []
        self._links_doc = []
        self._links = []
        self.render_obj = None

    def _clean(self,name):
        name=name.replace("/",".")
        name=name.strip(".")
        return j.core.text.strip_to_ascii_dense(name)

    def _get_file_path_new(self,name="",extension="jpeg"):
        nr=0
        if name=="":
            name=self.name
        dest = "%s/%s.%s"%(self.path_dir,name,extension)
        found = j.sal.fs.exists(dest)
        while found:
            nr+=1
            name = "%s_%s"%(name,nr) #to make sure we have a unique name
            dest = "%s/%s.%s"%(self.path_dir,name,extension)
            fname= "%s.%s"%(name,extension)
            found = j.sal.fs.exists(dest) or fname in self.docsite._files
        fname= "%s.%s"%(name,extension)
        self.docsite._files[fname]=dest
            
        return name,dest

    @property
    def links(self):
        if self._links == []:
            self._links_process()
        return self._links

    @property
    def images(self):
        if not self._images:
            self._links_process()
        return self._images


    @property
    def extension(self):
        if not self._extension:
           self._extension = j.sal.fs.getFileExtension(self.path)        
        return self._extension

    @property
    def title(self):
        if "title" in self.data:
            return self.data["title"]
        else:
            self.error_raise("Could not find title in doc.")

    def error_raise(self, msg):
        return self.docsite.error_raise(msg, doc=self)            

    def htmlpage_get(self,htmlpage=None):
        if htmlpage is None:
            htmlpage = j.data.html.page_get()
        htmlpage = self.markdown_obj.htmlpage_get(htmlpage=htmlpage, webparts=True)
        return htmlpage

    def html_get(self,htmlpage=None):
        return str(self.htmlpage_get(htmlpage=htmlpage))

    @property
    def html(self):
        return self.html_get()

    @property
    def data(self):
        if self._data=={}:

            #look for parts which are data
            for part in self.parts_get(cat="data"):
                for key,val in part.ddict.items():
                    print("data update")
                    if j.data.types.list.check(val):
                        if key not in self._data:
                            self._data[key] = []
                        for subval in val:
                            if subval not in self._data[key] and subval != "":
                                self._data[key].append(subval)
                    else:
                        self._data[key] = val

            #now we have all data from the document itself

            keys = [part for part in self.docsite.data_default.keys()]
            keys.sort(key=len)
            for key in keys:
                key = key.strip("/")
                if self.path_rel.startswith(key):
                    data = self.docsite.data_default[key]
                    self._data_update(data)
            print("data process doc")


        return self._data

    @property
    def markdown_obj(self):
        if not self._md:
            try:
                self._md = j.data.markdown.document_get(self.markdown_source)
            except Exception as e:
                msg = "Could not parse markdown of %s"%self
                msg += str(e)
                self.error_raise(msg)
                self._md = j.data.markdown.document_get(content="```\n%s\n```\n"%msg)
        return self._md

    def header_get(self, level=1, nr=0):
        res = self.markdown_obj.parts_get(cat="header")
        if len(res)<1:
            return self.error_raise("header level:%s %s could not be found"%(level,nr))
        for header in res:
            if header.level == level:
                return header

    def dynamic_process(self,url):
        self.kwargs = {}
        if "?" in url:
            # query=url.split("?",1)[1]
            query=urlparse(url).query
            kwargs=parse_qsl(query)
            for key,val in kwargs:
                self.kwargs[key]=val
        return self.markdown

    @property
    def markdown(self):
        """
        markdown after processing of the full doc
        """
        self._macros_process()
        self._links_process()
        try:
            res = self.markdown_obj.markdown
        except Exception as e:
            msg = "Could not parse markdown of %s"%self
            msg += str(e)
            self.error_raise(msg)
            res = msg

        if "{{" in res:
            #TODO:*1 rendering does not seem to be ok
            res = j.tools.jinja2.template_render(text=res, obj=self.render_obj, **self.data)
        return res

    @property
    def markdown_source(self):
        """
        markdown coming from source
        """
        if not self._content:
            self._content = j.sal.fs.readFile(self.path)
        return self._content

    @property
    def markdown_clean(self):
        # remove the code blocks (comments are already gone)
        print('markdown_clean')
        from IPython import embed;embed(colors='Linux')
        return None

    @property
    def markdown_clean_summary(self):
        c = self.content_clean
        lines = c.split("\n")
        counter = 0
        out = ""
        while counter < 20 and counter < len(lines):
            line = lines[counter]
            counter += 1
            if line.strip() == "" and counter > 10:
                return out
            if len(line) > 0 and line.strip()[0] == "#" and counter > 4:
                return out
            out += "%s\n" % line
        return out

    def _data_update(self, data):
        res = {}
        for key, valUpdate2 in data.items():
            # check for the keys not in the self.data yet and add them, the others are done above
            if key not in self._data:
                self._data[key] = copy.copy(valUpdate2)  # needs to be copy.copy otherwise we rewrite source later


    def link_get(self,filename=None,cat=None,nr=0,die=True):
        """
        @param cat: image, doc,link, officedoc, imagelink  #doc is markdown
        """
        res = self.links_get(filename=filename, cat=cat)
        if len(res)== 0:
            if die:
                raise RuntimeError("could not find link %s:%s"%(filename,cat))
            else:
                return None
        if nr>len(res):
            if die:
                raise RuntimeError("could not find link %s:%s at position:%s"%(filename,cat,nr))
            else:
                return None            
        return res[nr]

    def links_get(self,filename=None,cat=None):  
        self._links_process()
        res=[]
        for link in self._links:
            found=True
            if cat is not None and not link.cat==cat:
                found = False
            if filename is not None and not link.filename.startswith(filename):
                found = False
            if found:
                res.append(link)
        return res

    def _args_get(self,methodcode):
        methodcode = methodcode.split("(", 1)[1]
        methodcode = methodcode.rstrip(", )")  # remove end )
        args = [ item.strip().strip("\"").strip("'").strip() for item in methodcode.split(",") if item.find("=")==-1]
        return args

    def _kwargs_get(self, methodcode):
        if "(" in methodcode:
            methodcode = methodcode.split("(", 1)[1]
            methodcode = methodcode.rstrip(", )")  # remove end )
        kwargs_ = [ item.strip() for item in methodcode.split(",") if item.find("=")!=-1]
        if kwargs_ != []:
            kw={}
            for item in kwargs_:
                pre,post=item.split("=",1)
                kw[pre.strip()]=eval(post)
            return kw
        else:
            return {}

    def _macros_process(self):
        """
        eval the macros
        """

        for part in self.parts_get(cat="macro"):
            if part.method.strip()=="":
                return self.docsite.error_raise("empty macro cannot be executed", doc=self)

            macro_name = part.method.split("(",1)[0].strip()

            if not macro_name in j.tools.markdowndocs._macros:
                e = "COULD NOT FIND MACRO"
                block = "```python\nERROR IN MACRO*** TODO: *1 ***\nmacro:\n%s\nERROR:\n%s\n```\n" % (macro_name, e)
                self._logger.error(block)
                self.docsite.error_raise(block, doc=self)

            method = j.tools.markdowndocs._macros[macro_name]
            args = self._args_get(part.method)
            kwargs = self._kwargs_get(part.method)

            # j.shell()
            try:
                part.result = method(self,*args,**kwargs,content=part.data)
            except Exception as e:                
                block = "```python\nERROR IN MACRO*** TODO: *1 ***\nmacro:\n%s\nERROR:\n%s\n```\n" % (macro_name, e)
                self._logger.error(block)
                self.docsite.error_raise(block, doc=self)    
                part.result = block

    def _links_process(self):
        """
        results in:
            self._images = []
            self._links_external = []
            self._links_doc = 
        """
        if not self._links == []:
            return
        # check links for internal images
        # regex = "!+\[.*\] *\([a-zA-Z0-9\.\-\_\ \/\"]+\)"  # find all possible images/links
        regex = "!*\[.*\] *\(.*\)"
        for match in j.data.regex.yieldRegexMatches(regex, self.markdown_source, flags=0):
            self._logger.debug("##:file:link:%s" % match)
            link = Link(self,match.founditem)
            if not link.link_source=="":
                self._links.append(link)
    

        #whats this one?
        # regex = "src *= *\" */?static"
        # for match in j.data.regex.yieldRegexMatches(regex, self.markdown_source, flags=0):
        #     self._content = self.markdown_source.replace(match.foundpart, "src = \"/")

    def part_get(self,text_to_find=None,cat=None,nr=0,die=True):
        """
        return part of markdown document e.g. header

        @param cat is: table, header, macro, code, comment1line, comment, block, data, image
        @param nr is the one you need to have 0 = first one which matches
        @param text_to_find looks into the text
        """        
        return self.markdown_obj.part_get(text_to_find=text_to_find,cat=cat, nr=nr,die=die)

    def parts_get(self,text_to_find=None,cat=None):  
        """
        @param cat is: table, header, macro, code, comment1line, comment, block, data, image
        @param text_to_find looks into the text
        """         
        return self.markdown_obj.parts_get(text_to_find=text_to_find,cat=cat)

    def __repr__(self):
        return "doc:%s:%s" % (self.name, self.path)

    __str__ = __repr__


