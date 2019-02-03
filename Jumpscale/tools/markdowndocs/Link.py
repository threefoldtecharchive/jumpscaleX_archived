from Jumpscale import j
import toml

import copy

JSBASE = j.application.JSBaseClass


# Some links that needs to be skipped from verifying because the crawling is forbidden
SKIPPED_LINKS = ['t.me', 'chat.grid.tf', 'linkedin.com', 'docs.grid.tf', 'btc-alpha',
                 'kraken.com', 'bitoasis.net', 'cex.io',  'itsyou.online', 'skype:',
                 'medium.com', "mailto:"]

class Link(j.application.JSBaseClass):
    def __init__(self,doc, source):
        JSBASE.__init__(self)        
        self.docsite = doc.docsite
        self.doc = doc
        self.extension = ""
        self.source = source #original text
        self.cat = ""  #category in image,doc,link,officedoc, imagelink  #doc is markdown
        self.link_source = "" #text to replace when rewrite is needed
        self.link_source_original = "" #original link
        self.error_msg = ""
        self.filename = ""
        self.filepath = ""
        self.link_descr="" #whats inside the []
        self.link_to_doc = None
        self._process()

    def _clean(self,name):
        return j.core.text.convert_to_snake_case(name)

    def error(self,msg):
        self.error_msg = msg
        msg="**ERROR:** problem with link:%s\n%s"%(self.source,msg)        
        # self._logger.error(msg)
        self.docsite.error_raise(msg, doc=self.doc)
        self.doc._content = self.doc._content.replace(self.source,msg) 
        return msg

    def _process(self):
        self.link_source = self.source.rsplit("(",1)[1].split(")",1)[0] #find inside ()
        self.link_source = self.link_source.replace("\"","").replace("'","")
        self.link_descr = self.source.split("[",1)[1].split("]",1)[0].replace("\"","").replace("'","") #find inside []

        if self.link_source.strip()=="":
            return self.error("link is empty, but url is:%s"%self.source)

        
        if "@" in self.link_descr:
            self.link_source_original = self.link_descr.split("@")[1].strip() #was link to original source
            self.link_descr = self.link_descr.split("@")[0].strip()
            
        if "?" in self.link_source:
            lsource=self.link_source.split("?",1)[0]
        else:
            lsource =self.link_source


        self.extension = j.sal.fs.getFileExtension(lsource)

        if "http" in self.link_source or "https" in self.link_source:
            self.link_source_original = self.link_source            
            if self.source.startswith("!"):
                if "?" in self.link_source:
                   link_source=self.link_source.split("?",1)[0]
                else:
                    link_source=self.link_source
                self.filename = self._clean(j.sal.fs.getBaseName(link_source))

                if not self.extension in ["png", "jpg", "jpeg", "mov", "mp4","mp3","docx"]:
                    self.extension = "jpeg" #to support url's like https://images.unsplash.com/photo-1533157961145-8cb586c448e1?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=4e252bcd55caa8958985866ad15ec954&auto=format&fit=crop&w=1534&q=80
                    self.filename = self.filename + '.jpeg'

                if j.sal.fs.getFileExtension(self.filename)!=self.extension:
                    j.shell()
            else:
                #check link exists
                self.cat = "link"
                if self.docsite.links_verify:
                    self.link_verify()

                self.filename = None #because is e.g. other site


        else:
            if self.link_source.strip() == "/":
                self.link_source = ""
                return
            if "#" in self.link_source:
                self.link_source = ""
                return

            if "?" in self.link_source:
                self.link_source=self.link_source.split("?",1)[0]
                
            if self.link_source.find("/") != -1 and self.extension != "md":
                name = self.link_source.split("/")[-1]
            else:
                name = self.link_source

            self.filename = self._clean(name) #cleanly normalized name but extension still part of it
            #e.g. balance_inspiration_motivation_life_scene_wander_big.jpg
            if self.filename.strip()=="":
                return self.error("filename is empty")

            #only possible for images (video, image)
            if self.source.startswith("!"):
                self.cat = "image"
                if not self.extension in ["png", "jpg", "jpeg", "mov", "mp4"]:
                    return self.error("found unsupported image file: extension:%s"%self.extension)

            if self.cat =="":
                if self.extension in ["png", "jpg", "jpeg", "mov", "mp4"]:
                    self.cat = "imagelink"
                elif self.extension in ["doc", "docx", "pdf", "xls", "xlsx", "pdf"]:
                    self.cat = "officedoc"
                elif self.extension in ["md","",None]:
                    self.cat = "doc" #link to a markdown document
                    try:
                        self.link_to_doc =  self.docsite.doc_get(self.link_source ,die=True)
                    except Exception as e:
                        if "Cannot find doc" in str(e):
                            return self.error(str(e))
                        raise e
                else:
                    # j.shell()
                    return self.error("found unsupported extension")

            self.filepath = self.doc.docsite.file_get(self.filename, die=False)



    
    @property
    def markdown(self):
        if self.source.startswith("!"):
            c="!"
            if self.link_source_original is not "":
                descr="%s@%s"%(self.link_descr,self.link_source_original )
            else:
                descr=self.link_descr
        else:
            c=""
            descr=self.link_descr
        c+= "[%s](%s)"%(descr,self.link_source)
        return c

    def download(self,dest):
        if not "http" in self.link_source:
            return
        self._logger.info("download:%s\n%s"%(self.link_source_original,dest))
        ddir = j.sal.fs.getDirName(dest)
        if not j.sal.fs.exists(dest):
            cmd = "cd %s;rm -f %s;curl '%s' -o '%s'"%(ddir,dest,self.link_source_original,dest) #cannot use primitive something wrong sometimes with ssl verification
            j.sal.process.execute(cmd, die=False)

    def link_verify(self):
        def do():
            if any(link in self.link_source for link in SKIPPED_LINKS):
                return True
            self._logger.info("check link exists:%s"%self.link_source)
            if not j.clients.http.ping(self.link_source_original):
                self.error("link not alive:%s"%self.link_source_original)                
                return False
            return True                 
        res =  self._cache.get(self.link_source, method=do, expire=3600)
        if res is not True:
            self.error(res)
            return False

    def replace_in_txt(self,txt):
        if len(self.source)<4:
            j.shell()
            raise RuntimeError("something wrong with original source")
        txt = txt.replace(self.source,self.markdown)
        # self.source = self.markdown #there is a new source now
        return txt

    def __repr__(self):
        if self.cat == "link":
            return "link:%s:%s" % (self.cat, self.link_source)
        else:
            return "link:%s:%s" % (self.cat, self.filename)

    __str__ = __repr__

