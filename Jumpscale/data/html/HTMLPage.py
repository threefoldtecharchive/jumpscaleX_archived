from Jumpscale import j
# import copy

JSBASE = j.application.JSBaseClass

class HTMLPage(JSBASE):

    """
    the methods add code to the self.body part !!!!!
    """

    def __init__(self, ):
        """
        """
        JSBASE.__init__(self)
        self.content = ""

        # self.currentlinenr = len(self.content.split("\n")) + 1

        self.head = ""
        self.tail = ""
        self.body = ""
        
        self.divlevel = []

        self._inBlock = False
        self._inBlockType = ""
        self._inBlockClosingStatement = ""
        
        self._listslevel = 0

        self._codeblockid = 0

        #reused everywhere to make sure we don't add doubles
        self._contentAddedCheck=[]

        self.padding = True

        # self.pagemirror4jscss = None

        self.processparameters = {}
        self.bodyattributes = []

        self.liblocation = "/static/"
        
        # self._hasCharts = False
        # self._hasCodeblock = False
        # self._hasSidebar = False
        
        # self.functionsAdded = {}
        self._explorerInstance = 0
        self._lineId = 0
        self._enableprettyprint = False
        # self.documentReadyFunctions = []

    def _contentExistsCheck(self,content):
        """
        checks if content was already added if ues return True
        """
        content = content.lower()
        content = content.replace("\n","").replace(" ","").replace("\t","").replace("\"","").replace("'","").replace("`","")
        md5 = j.data.hash.md5_string(content)
        if md5 in self._contentAddedCheck:
            return True
        self._contentAddedCheck.append(md5)
        return False
            
            
        

    def part_add(self, part, newline=False, isElement=True, blockcheck=True):
        if blockcheck:
            # print ("blockcheck %s" % part)
            self._checkBlock("", "", "")
        # else:
            # print ("no blockcheck %s" % part)
        part = str(part)
        part = part.replace("text:u", "")
        part.strip("'")
        part = part.strip()
        part = part.replace("\r", "")
        if part != '' and isElement:
            part = "%s" % part
        elif newline and part != '':
            part = "<p>%s</p><br/>" % part
        elif newline and part == '':
            part = '<br/>'
        elif part == "":
            pass
        else:
            part = "<p>%s</p>" % part

        part = part.replace("&lt;br&gt;", "<br />")

        if part != "":
            self.body = "%s%s\n" % (self.body, part)

    def paragraph_add(self, part):
        self.part_add(part, isElement=False)

    # def addFavicon(self, href, type):
    #     self.favicon = '<link rel="shortcut icon" type="%s" href="%s" />' % (type, href)

    def listitem_add(self, part, level=1, list_type='list', tag='ul', attributes=''):
        self._checkBlock(list_type, "", "</{0}>".format(tag))
        if level > self._listslevel:
            for i in range(level - self._listslevel):
                self.part_add("<{0} {1}>".format(tag, attributes), blockcheck=False)
            self._listslevel = level
        if level < self._listslevel:
            for i in range(self._listslevel - level):
                self.part_add("</{0}>".format(tag), blockcheck=False)
            self._listslevel = level
        self.part_add("<li>%s</li>" % part, blockcheck=False)

    def _checkBlock(self, ttype, open, close):
        """
        types are : list,descr
        """
        # print "checkblock inblock:%s ttype:%s intype:%s" %(self._inBlock,ttype,self._inBlockType)
        if self._inBlock:
            if self._inBlockType != ttype:
                if self._inBlockType in ("list", "number"):
                    for i in range(self._listslevel):
                        self.part_add(self._inBlockClosingStatement, blockcheck=False)
                    self._listslevel = 0
                else:
                    self.part_add(self._inBlockClosingStatement, blockcheck=False)
                if open != "":
                    self.part_add(open, blockcheck=False)
                    self._inBlock = True
                    self._inBlockType = ttype
                    self._inBlockClosingStatement = close
                else:
                    self._inBlock = False
                    self._inBlockType = ""
                    self._inBlockClosingStatement = ""
        else:
            self.part_add(open, blockcheck=False)
            if ttype != "" and close != "":
                self._inBlock = True
                self._inBlockType = ttype
                self._inBlockClosingStatement = close
        # print "checkblock END: inblock:%s ttype:%s intype:%s" %(self._inBlock,ttype,self._inBlockType)

    # def addDescr(self, name, descr):
    #     self._checkBlock("descr", "<dl class=\"dl-horizontal\">", "</dl>")
    #     self.part_add("<dt>%s</dt>\n<dd>%s</dd>" % (name, descr), blockcheck=False)

    def list_add(self, parts, level=1):
        """
        parts: list of list_items
        only works on 1 level
        """

        # todo: figure a way for nested lists!!
        lists = '<ul>'
        for part in parts:
            lists += '\n<li>%s</li>' % part
        lists += '\n</ul>'
        self.part_add(lists, blockcheck=False)

    def newline_add(self, nrlines=1):
        for line in range(nrlines):
            self.part_add("", True, isElement=True)

    def header_add(self, part, level=1):
        part = str(part)

        header = "<h%s class=\"title\">%s</h%s>" % (level, part, level)
        self.part_add(header, isElement=True)

    def table_add(self, rows, headers="", showcolumns=[], columnAliases={}, classparams="table-condensed table-hover", linkcolumns=[]):
        """
        @param rows [[col1,col2, ...]]  (array of array of column values)
        @param headers [header1, header2, ...]
        @param linkcolumns has pos (starting 0) of columns which should be formatted as links  (in that column format needs to be $description__$link
        """
        if rows == [[]]:
            return
        if "datatables" in self.functionsAdded:
            classparams += 'cellpadding="0" cellspacing="0" border="0" class="table table-striped table-bordered display dataTable'
            if headers:
                classparams += ' JSdataTable'
        if len(rows) == 0:
            return False
        l = len(rows[0])
        if str(headers) != "" and headers is not None:
            if l != len(headers):
                headers = [""] + headers
            if l != len(headers):
                print("Cannot process headers, wrong nr of cols")
                self.part_add("ERROR header wrong nr of cols:%s" % headers)
                headers = []

        c = "<table  class='table %s'>\n" % classparams  # the content
        if headers != "":
            c += "<thead><tr>\n"
            for item in headers:
                if item == "":
                    item = " "
                c = "%s<th>%s</th>\n" % (c, item)
            c += "</tr></thead>\n"
        rows3 = copy.deepcopy(rows)
        c += "<tbody>\n"
        for row in rows3:
            c += "<tr>\n"
            if row and row[0] in columnAliases:
                row[0] = columnAliases[row[0]]
            colnr = 0
            for col in row:
                if col == "":
                    col = " "
                if colnr in linkcolumns:
                    if len(col.split("__")) != 2:
                        raise RuntimeError(
                            "column which represents a link needs to be of format $descr__$link, here was:%s" %
                            col)
                    c += "<td>%s</td>\n" % self.link_get(col.split("__")[0], col.split("__")[1])
                else:
                    c += "<td>%s</td>\n" % self.getRound(col)
                colnr += 1
            c += "</tr>\n"
        c += "</tbody></table>\n\n"
        self.part_add(c, True, isElement=True)

    def dict_add(self, dictobject, description="", keystoshow=[], aliases={}, roundingDigits=None):
        """
        @params aliases is dict with mapping between name in dict and name to use
        """
        if keystoshow == []:
            keystoshow = list(dictobject.keys())
        self.part_add(description)
        arr = []
        for item in keystoshow:
            if item in aliases:
                name = aliases[item]
            else:
                name = item
            arr.append([name, dictobject[item]])
        self.list_add(arr)
        self.newline_add()

    @staticmethod
    def _link_get(description, link, link_id=None, link_class=None, htmlelements="", newtab=False):
        if link_id:
            link_id = ' id="%s"' % link_id.strip()
        else:
            link_id = ''

        if link_class:
            link_class = ' class="%s"' % link_class.strip()
        else:
            link_class = ''

        if newtab:
            target = 'target="_blank"'
        else:
            target = ''

        anchor = "<a href='%s' %s %s %s %s>%s</a>" % (link.strip(),
                                                      link_id.strip(),
                                                      link_class,
                                                      htmlelements,
                                                      target,
                                                      description)
        return anchor

    def link_add(self, description, link, newtab=False):
        anchor = self._link_get(description, link, newtab=newtab)
        self.paragraph_add(anchor)

    def pagebreak_add(self,):
        self.part_add("<hr style='page-break-after: always;'/>")

    def combobox_add(self, items):
        """
        @items is a list of tuples [ ('text to show', 'value'), ]
        """
        import random
        if items:
            id = ('dropdown%s' % random.random()).replace('.', '')
            html = '<select id=%s>\n' % (id)

            for text, value in items:
                html += '<option value="%s">%s</option>\n' % (value, text)
            html += '</select>'
            self.html_add(html)
            return id
        else:
            return ''

    def bootstrapcombobox_add(self, title, items, id=None):
        self.addBootstrap()
        html = """
        <div class="btn-group" ${id}>
        <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            ${title}<span class="caret"></span>
        </button>
        <ul class="dropdown-menu">
            {% for name, action in items %}
            <li><a href="javascript:void(0)" onclick="${action}">${name}</a></li>
            {% endfor %}
        </ul>
        </div>
        """
        html=j.core.text.strip(html)
        id = 'id="%s"' % id if id else ''
        html = self.jenv.from_string(html).render(items=items, title=title, id=id)
        self.html_add(html)

    def actionbox_add(self, actions):
        """
        @actions is array of array, [[$actionname1,$params1],[$actionname2,$params2]]
        """
        row = []
        for item in actions:
            action = item[0]
            actiondescr = item[1]
            if actiondescr == "":
                actiondescr = action
            params = item[2]

            if action in self.actions:
                link = self.actions[action]
                link = link.replace("{params}", params)
                row.append(self.link_get(actiondescr, link))
            else:
                raise RuntimeError("Could not find action %s" % action)
        self.list_add([row])

    @staticmethod
    def _format_styles(styles):
        """
        Return CSS styles, given a list of CSS attributes
        @param styles a list of tuples, of CSS attributes, e.g. [("background-color", "green), ("border", "1px solid green")]

        >>> PageHTML._format_styles([("background-color", "green"), ("border", "1px solid green")])
        'background-color: green; border: 1px solid green'
        """
        try:
            return '; '.join('{0}: {1}'.format(*style) for style in styles)
        except IndexError:
            return ''

    def image_add(self, title, imagePath, width=None, height=None, styles=[]):
        """
        @param title alt text of the image
        @param imagePath can be url or local path
        @param width width of the image
        @param height height of the image
        @param styles a list of tuples, containing CSS attributes for the image, e.g. [("background-color", "green), ("border", "1px solid green")]
        """
        width_n_height = ''
        if width:
            width_n_height += ' width="{0}"'.format(width)
        if height:
            width_n_height += ' height="{0}"'.format(height)

        img = "<img src='%s' alt='%s' %s style='clear:both;%s' />" % (
            imagePath, title, width_n_height, PageHTML._format_styles(styles))
        self.part_add(img, isElement=True)

    def tablewithcontent_add(self, columnsWidth, colContents):
        """
        @param columnsWidth = Array with each element a nr, when None then HTML does the formatting, otherwise relative to each other
        @param colContents = array with each element HTML code
        """
        table = "<table><thead><tr>"
        for colWidth, colContent in zip(columnsWidth, colContents):
            if colWidth:
                table += "<th width='%s'>%s</th>" % (colWidth, colContent)
            else:
                table += "<th>%s</th>" % (colContent)
        table += "</tr></head></table>"
        self.part_add(table, isElement=True)

    def html_add(self, htmlcode):
        #import cgi
        #html = "<pre>%s</pre>" % cgi.escape(htmlcode)
        self.part_add(htmlcode, isElement=False)

    def css_remove_all(self, exclude, permanent=False):
        """
        will walk over header and remove css links
        link need to be full e.g. bootstrap.min.css
        """
        out = ""
        for line in self.head.split("\n"):
            if line.lower().find(exclude) == -1:
                out += "%s\n" % line
        self.head = out
        if permanent:
            key = exclude.strip().lower()
            self.jscsslinks[key] = True

    def css_add(self, cssLink=None, cssContent=None, exlcude="", media=None):
        """
        """
        #TODO:*1 what is this?
        # if self.pagemirror4jscss is not None:
        #     self.pagemirror4jscss.css_add(cssLink, cssContent)
        # if cssLink is not None:
        #     key = cssLink.strip().lower() + (media or '')
            # if key in self.jscsslinks:
            #     return
            # self.jscsslinks[key] = True

        mediatag = ""
        if media:
            mediatag = "media='%s'" % media
        css = ""
        if cssContent:
            if not self._contentExistsCheck(cssContent):
                css = "\n<style type='text/css' %s>%s\n</style>\n" % (mediatag, cssContent)
        else:
            if not self._contentExistsCheck(cssLink+mediatag):
                css = "<link  href='%s' type='text/css' rel='stylesheet' %s/>\n" % (cssLink, mediatag)
        self.head += css

    def timestamp_add(self, classname='jstimestamp'):
        js = """
        $(function() {
            var updateTime = function () {
                $(".%s").each(function() {
                    var $this = $(this);
                    var timestmp = parseFloat($this.data('ts'));
                    if (timestmp > 0)
                        var time = new Date(timestmp * 1000).toLocaleString();
                    else var time = "";
                    $this.html(time);
                });
            };
            updateTime()
            window.updateTime = updateTime;
            $(document).ajaxComplete(updateTime);
        });
        """ % classname
        if classname not in self._timestampsAdded:
            self.js_add(jsContent=js)
            self._timestampsAdded.add(classname)

    def js_add(self, jsLink=None, jsContent=None, header=True):
        # if self.pagemirror4jscss is not None:
        #     self.pagemirror4jscss.js_add(jsLink, jsContent, header)
        # if jsLink is not None:
        #     key = jsLink.strip().lower()
        #     if key in self.jscsslinks:
        #         return
        #     self.jscsslinks[key] = True
        js=""
        if jsContent:
            if not self._contentExistsCheck(jsContent):
                js = "<script type='text/javascript'>\n%s</script>\n" % jsContent
        else:
            if not self._contentExistsCheck(jsLink):
                js = "<script src='%s' type='text/javascript'></script>\n" % jsLink
            #js = "<script  src='%s' </script>\n" % jsLink
        if header:
            self.head += js
        else:
            self.tail += js

    def js_remove(self, jsLink=None, jsContent=None):
        out = ""
        js = ''
        if jsContent:
            js = "<script type='text/javascript'>\n%s</script>\n" % jsContent
        else:
            js = "<script  src='%s' type='text/javascript'></script>\n" % jsLink
        self.head = self.head.replace(js.strip(), '')
        self.body = self.body.replace(js.strip(), '')

    # def scriptbody_add(self, jsContent):
    #     self.scriptBody = "%s%s\n" % (self.scriptBody, jsContent)

    def jquery_add(self):
        #TODO: *1 fix
        self.js_add('/static/jquery/jquery.min.js')
        self.js_add("/static/jquery/jquery-ui.min.js")

    def bootstrap3_add(self, jquery=True):
        if jquery:
            self.jquery_add()

        self.js_add('/static/bootstrap3/bootstrap.min.js')
        self.css_add('/static/bootstrap3/bootstrap.min.css')

    def bootstrap4_add(self, jquery=True):
        if jquery:
            self.jquery_add()

        self.js_add('/static/bootstrap4/bootstrap.min.js')
        self.css_add('/static/bootstrap4/bootstrap.min.css')

    def bodyattribute_add(self, attribute):
        if attribute not in self.bodyattributes:
            self.bodyattributes.append(attribute)

    def document_readyfunction_add(self, function): #TODO: dont understand
        """
        e.g. $('.dataTable').dataTable();
        """
        if self.pagemirror4jscss is not None:
            self.pagemirror4jscss.document_readyfunction_add(function)
        if function not in self.documentReadyFunctions:
            self.documentReadyFunctions.append(function)

    def _htmlheader_add(self, header):
        self.head += header

    def _htmlbody_add(self, body):
        self.body += body

    def accordion_add(self, panels):
        self.js_add('/static/codemirror/autorefresh.js', header=False)
        self.part_add('<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">')

        panels.sort(key=lambda x: x['title'])

        for panel_data in panels:
            if panel_data is None:
                continue

            content = panel_data['content']

            for item in ['header_id', 'section_id', 'label_id', 'label_icon', 'label_color']:
                if item not in panel_data:
                    panel_data[item] = j.data.idgenerator.generateXCharID(10)

            self.part_add("""
            <div class="panel panel-default">
              <div class="panel-header" role="tab" id="%(header_id)s">
                <h4 class="panel-title">
                  <a data-toggle="collapse" data-parent="#accordion" href="#%(section_id)s" aria-expanded="true" aria-controls="%(section_id)s">%(title)s</a>
            """ % panel_data)

            if 'label_content' in panel_data:
                self.part_add("""
                <a id=%(label_id)s class="label-archive label label-%(label_color)s glyphicon glyphicon glyphicon-%(label_icon)s pull-right">%(label_content)s</a>
                """ % panel_data)

            self.part_add("""
                </h4>
              </div>
              <div id="%(section_id)s" class="panel-collapse collapse" role="tabpanel" aria-labelledby="%(header_id)s">
                <div class="panel-body">
                """ % panel_data)

            if panel_data.get('code', False):
                self.addCodeBlock(content, edit=False, exitpage=True, spacename='', pagename='', linenr=True, autorefresh=True)
            else:
                self.part_add(content)

            self.part_add("""
                </div> <!-- panel body-->
              </div> <!-- panel collapse-->
            </div> <!-- panel default-->""")

        self.part_add('</div>')  # close panel-group

    def content_get(self):
        return str(self)

    def html_get(self):
        out="<!DOCTYPE html>\n"
        out+="<html>"
        if self.head:
            out+="<head>\n"
            out=out+self.head+"\n"
            out+="</head>\n"
        out+="<body>\n"
        out=out+self.body+"\n"
        out+="</body>\n"
        out=out+self.tail+"\n"
        out+="</html>"
        return out
               

    def __str__(self):
        self.part_add("")
        return self.body
        # make sure we get closures where needed (/div)

        # if self.documentReadyFunctions != []:
        #     CC = "$(document).ready(function() {\n"
        #     for f in self.documentReadyFunctions:
        #         CC += "%s\n" % f
        #     CC += "} );\n"
        #     jsHead += "<script type='text/javascript'>" + CC + "</script>"
        #TODO: *1

        
    __repr__ = __str__
