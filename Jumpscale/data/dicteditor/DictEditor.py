from Jumpscale import j

class DictEditor(j.application.JSBaseClass):

    def __init__(self,ddict):
        self._dict = ddict
        j.application.JSBaseClass.__init__(self)

    def __getattr__(self, name):
        if name.startswith("_"):
            return self.__dict__[name]
        if name not in self._dict:
            raise RuntimeError("cannot find name '%s' in "%name)
        return self._dict[name]

    def __dir__(self):
        return [item for item in self._dict.keys()]

    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name]=value
            return
        self._dict[name]=value

    def edit(self):
        path = j.core.tools.text_replace("{DIR_TEMP}/dicteditor.toml")
        toml=j.data.serializers.toml.dumps(self._dict)
        j.sal.fs.writeFile(path,toml)
        j.core.tools.file_edit(path)
        data_out = j.sal.fs.readFile(path)
        if toml != data_out:
            self._dict = j.data.serializers.toml.loads(data_out)
        j.sal.fs.remove(path)

    def view(self):
        path = j.core.tools.text_replace("{DIR_TEMP}/dicteditor.toml")
        toml=j.data.serializers.toml.dumps(self._dict)
        j.tools.formatters.print_toml(toml)

    def __str__(self):
        out = j.core.tools.text_replace("{RED}Dict Editor:\n\n",colors=True)
        for key,item in self._dict.items():
            out+=j.core.tools.text_replace("{RED}- {BLUE}%-25s:   {RESET}%s \n"%(key,item),colors=True)
        return out
    __repr__ = __str__


class DictEditorFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.data.dict_editor"

    def _init(self):


    def get(self,ddict):
        """
        return dicteditor where you can manipulate the dict items & edit/view in console
        :param ddict:
        :return:
        """
        return DictEditor(ddict)


    def test(self):
        """
        js_shell 'j.data.dict_editor.test()'
        :return:
        """
        import copy
        config = copy.copy(j.core.myenv.config) #to make sure we don't edit the jumpscale config file

        e=j.data.dict_editor.get(config)

        e.DIR_TEMP="/tmp_new"

        assert config["DIR_TEMP"]=="/tmp_new"

        schema = """
        @url = despiegk.test2
        llist2 = "" (LS)
        nr = 4
        date_start = 0 (D)
        description = ""
        cost_estimate = 0.0 #this is a comment
        llist = []
        enum = "red,green,blue" (E) #first one specified is the default one

        @url = despiegk.test3
        llist = []
        description = ""
        """
        s=j.data.schema.get(schema_text=schema)
        o=s.new()


        j.shell()
