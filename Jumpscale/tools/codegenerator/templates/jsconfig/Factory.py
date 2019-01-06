from Jumpscale import j



from .{PARENTCLASS} import {PARENTCLASS}

class {NAME}Factory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.data.docs"

    _CHILDCLASS = DocSite

    def _init(self):
        self._logger_enable()
        self._bcdb = j.data.bcdb.new("docs") #will be a BCDB custom for this one using sqlite


    def test(self):
        """
        js_shell 'j.data.{obj.name.lower()}.test()'
        :return:
        """

        ds = self.get(name="test")

        doc = ds.get_doc(name="page1")
        doc = ds.get_file(name="page1")


        ds.git_url = "https://github.com/threefoldfoundation/info_foundation/tree/development/docs"
        ds.update() #will get from github

        j.shell()
