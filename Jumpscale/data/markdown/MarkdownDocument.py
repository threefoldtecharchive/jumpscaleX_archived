from . import mistune
import copy
from Jumpscale import j
from .MarkdownComponents import *
JSBASE = j.application.JSBaseClass


class MarkdownDocument(j.application.JSBaseClass):

    def __init__(self, content="", path=""):
        JSBASE.__init__(self)
        if path != "":
            content = j.sal.fs.readFile(path)

        self._content = content.rstrip()+"\n"

        self.parts = []
        if self._content:
            self._parse()

    def table_add(self):
        """
        returns table which needs to be manipulated
        """
        t = MDTable()
        self.parts.append(t)
        return t

    def header_add(self, level, title):
        """
        """
        self.parts.append(MDHeader(level, title))

    def listpart_add(self, level, text):
        """
        """
        self.parts.append(MDListpart(level, text))

    def comment_add(self, text):
        """
        """
        self.parts.append(MDComment(text))

    def comment1line_add(self, text):
        """
        """
        self.parts.append(MDComment1Line(text))

    def block_add(self, text):
        """
        """
        self.parts.append(MDBlock(text))

    def code_add(self, text, lang):
        """
        """
        self.parts.append(MDCode(text, lang=lang))

    def data_add(self, ddict=None, toml="", yaml=""):
        if ddict is None:
            ddict = {}
        ddict = copy.copy(ddict)
        self.parts.append(MDData(ddict=ddict, toml=toml, yaml=yaml))

    def macro_add(self, method, data=""):
        self.parts.append(MDMacro(method=method, data=data))

    def _parse(self):

        state = ""
        block = ""

        # needed to calculate the level of the lists
        prevListLevel = 0
        curListLevel = 1

        listblocklines = []
        # substate = ""

        def block_add(block):
            if block.strip() != "":
                self.block_add(block)
            substate = ""
            state = ""
            return ""

        if not self.content or self.content.strip() == '':
            return

        for line in self.content.split("\n"):
            # HEADERS
            if line.startswith("#") and state == "":
                block = block_add(block)
                level = 0
                line0 = line
                while line0.startswith("#"):
                    level += 1
                    line0 = line0[1:]
                title = line0.strip()
                self.parts.append(MDHeader(level, title))
                continue

            linestripped = line.strip()

            if linestripped.startswith("<!--") and linestripped.endswith("-->") and state == "":
                comment_part = linestripped[4:-3].strip()
                self.comment1line_add(comment_part)
                block = ""
                state = ""
                continue

            if line.startswith("!!!") and state == "":  # is 1 line macro
                lang = ""
                self.codeblock_add(line, lang=lang)
                continue

            if line.startswith("<!-"):
                state = "COMMENT"
                continue

            # process all comment states
            if state.startswith("COMMENT"):
                if line.startswith("-->"):
                    state = ""
                    if state == "COMMENT":
                        self.parts.append(MDComment(block))
                    block = ""
                    continue
                block += "%s\n" % line

            # LIST
            if linestripped.startswith("-") or linestripped.startswith("*") and state in ["", "LIST"]:
                state = "LIST"
                listblocklines.append(line)
                continue
            else:
                # get out of state state
                if state == "LIST":
                    state = ""
                    self.parts.append(MDList("\n".join(listblocklines)))
                    listblocklines = []

            if state == "TABLE" and not linestripped.startswith("|"):
                state = ""
                self.parts.append(table)
                table = None
                cols = []

            # TABLE
            if state != "TABLE" and linestripped.startswith("|"):
                state = "TABLE"
                block = block_add(block)
                cols = [part.strip()
                        for part in line.split("|") if part.strip() != ""]
                table = MDTable()
                table.header_add(cols)
                continue

            if state == "TABLE":
                if linestripped.startswith("|") and linestripped.endswith("|") and line.find("---") != -1:
                    continue
                cols = [part.strip() for part in line.strip().strip('|').split("|")]
                table.row_add(cols)
                continue

            # if linestripped.find("python2")!=-1:
            #     from pudb import set_trace; set_trace()

            # CODE
            if state == "":
                if linestripped.startswith("```") or linestripped.startswith("'''"):
                    block = block_add(block)
                    state = "CODE"
                    lang = line.strip("'` ")
                    if linestripped.startswith("```"):
                        end = "```"
                    else:
                        end = "'''"
                    continue

            if state == "CODE":
                if linestripped.startswith(end):
                    state = ""
                    self.codeblock_add(block, lang=lang)
                    block = ""
                    lang = ""
                    end = ""
                else:
                    block += "%s\n" % line
                continue

            if linestripped != "":
                block += "%s\n" % line
            block = block_add(block)

    def codeblock_add(self, block, lang=""):
        """
        add the full code block
        """
        lang = lang.lower().strip()
        c = block.strip().split("\n")[0].lower()
        if c.startswith("!!!data") and lang in ["toml", "yaml"]:
            # is data
            block = "\n".join(block.strip().split("\n")[1:])+"\n"
            if lang == "toml":
                self.data_add(toml=block)
            elif lang == "yaml":
                self.data_add(yaml=block)
            else:
                raise RuntimeError("could not add codeblock for %s" % block)
        elif c.startswith("!!!") and lang == "":
            method = block.strip().split("\n")[0][3:].strip()  # remove !!!
            data = "\n".join(block.strip().split("\n")[1:])+"\n"
            if "(" in method:
                data2 = data
            else:
                data = data.replace("True", "true")
                data = data.replace("False", "false")
                if data.strip() != "":
                    try:
                        data2 = j.data.serializers.toml.loads(data)
                    except RuntimeError:
                        data2 = {'content': data}
                else:
                    data2 = {}
            self.macro_add(method=method, data=data2)
        else:
            self.code_add(text=block, lang=lang)

    @property
    def content(self):
        return self._content

    @property
    def markdown(self):
        out = ""
        prevtype = ""
        for part in self.parts:
            if part.type not in ["list"]:
                if prevtype == "list":
                    out += "\n"
                out += part.markdown.rstrip() + "\n\n"
            else:
                out += part.markdown.rstrip() + "\n"

            prevtype = part.type
        return out

    def __repr__(self):
        out = ""
        for part in self.parts:
            part0 = str(part).rstrip("\n")+"\n\n"
            out += part0
        return out

    __str__ = __repr__

    def part_get(self, text_to_find=None, cat=None, nr=0, die=True):
        """
        @param cat is: table, header, macro, code, comment1line, comment, block, data, image
        @param nr is the one you need to have 0 = first one which matches
        @param text_to_find looks into the text
        """
        res = self.parts_get(text_to_find=text_to_find, cat=cat)
        if len(res) == 0:
            if die:
                raise RuntimeError("could not find part %s:%s" % (text_to_find, cat))
            else:
                return None
        if nr > len(res):
            if die:
                raise RuntimeError("could not find part %s:%s at position:%s" % (text_to_find, cat, nr))
            else:
                return None
        return res[nr]

    def parts_get(self, text_to_find=None, cat=None):
        """
        @param cat is: table, header, macro, code, comment1line, comment, block, data, image
        @param text_to_find looks into the text
        """
        res = []
        for part in self.parts:
            found = True
            if cat is not None and not part.type.startswith(cat):
                found = False
            if text_to_find is not None and part.text.find(text_to_find) == -1:
                found = False
            if found:
                res.append(part)
        return res

    @property
    def html(self):
        return str(self.htmlpage_get())

    def pdf(self, path):
        """
        write pdf to path specified,

        :param path:
        :return:
        """
        raise NotImplemented()

    def htmlpage_get(self, htmlpage=None, webparts=True):
        """
        is the htmlpage, if not specified then its j.data.html.page_get()

        if webparts it will get them from https://github.com/threefoldtech/jumpscale_weblibs/tree/master/webparts

        """
        if webparts:
            j.data.html.webparts_enable()
        if not htmlpage:
            htmlpage = j.data.html.page_get()

        for part in self.parts:
            if part.type == "block":
                htmlpage.paragraph_add(mistune.markdown(part.markdown.strip()))
            elif part.type == "header":
                htmlpage.header_add(part.title, level=part.level)
            elif part.type == "code":
                # codemirror code generator
                j.data.html.webparts.codemirror_add(self=htmlpage, code=part.markdown)
            elif part.type == "table":
                # can also use htmlpage.table_add  #TODO: need to see whats best
                # there will be more optimal ways how to do this in future, with real javascript
                htmlpage.html_add(part.html)
            elif part.type == "data":
                pass
            elif part.type == "list":
                htmlpage.html_add(mistune.markdown(part.markdown))
            elif part.type == "macro":
                htmlpage.paragraph_add(mistune.markdown(part.markdown.strip()))
                # if j.tools.markdowndocs_loaded is not []:
                #     #means there is no doc generator so cannot load macro
                #     j.data.html.webparts.codemirror_add(self=htmlpage,code=part.text)
                # else:
                #     print("html_get from markdown, need to execute macro")
                #     from IPython import embed;embed(colors='Linux')
                #     s
            else:
                print("htmlpage_get")
                from IPython import embed
                embed(colors='Linux')
                s

        return htmlpage

    # def _findFancyHeaders(self):
    #     if not self.content or self.content.strip() == "":
    #         return
    #     out = []
    #     for line in self.content.split("\n"):
    #         if line.startswith("===="):
    #             out[-1] = "# %s" % out[-1]
    #             continue

    #         if line.startswith("-----"):
    #             out[-1] = "## %s" % out[-1]
    #             continue
    #         out.append(line)

    #     self._content = "\n".join(out)

        # def dataobj_get(self, ttype, guid):
    #     """
    #     ttype is name for the block
    #     guid is unique id, can be name or guid or int(id)

    #     """
    #     key = "%s__%s" % (ttype, guid)
    #     if key not in self._dataCache:
    #         self.datacollection_get()
    #     if key not in self._dataCache:
    #         raise j.exceptions.Input(
    #             "Cannot find object with type:%s guid:%s" % (ttype, guid))
    #     return self._dataCache[key].ddict

    # @property
    # def tokens(self):
    #     if self._tokens == "":
    #         bl = BlockLexer()
    #         self._tokens = bl.parse(self._content)
    #     return self._tokens

    # @tokens.setter
    # def tokens(self, val):
    #     self._changed_tokens = True
    #     self._tokens = val
