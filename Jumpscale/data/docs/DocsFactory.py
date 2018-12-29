from Jumpscale import j

from .DocSite import DocSite

class DocsFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.data.docs"

    _CHILDCLASS = DocSite

    def _init(self):
        self._logger_enable()


    def test(self):
        """
        js_shell 'j.data.docs.test()'
        :return:
        """

        ds = self.get(name="test")

        doc = ds.get(name="page1")




        j.shell()
