from Jumpscale import j
import os

# from data.markdown.mistune import *

# from pygments import highlight
# from pygments.lexers import get_lexer_by_name
# from pygments.formatters import HtmlFormatter

import copy

from .MarkdownDocument import *
from .MarkdownComponents import *
JSBASE = j.application.JSBaseClass


class MarkdownFactory(j.builder._BaseClass):

    def __init__(self):
        self.__jslocation__ = "j.data.markdown"
        JSBASE.__init__(self)

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))


    def document_get(self, content="", path=""):
        """
        returns a tool which allows easy creation of a markdown document
        """
        return MarkdownDocument(content, path)

    def mdtable_get(self):
        return MDTable()

    def mddata_get(self):
        return MDData()

    # def install_dependencies_pdf_generator(self):
    #     raise RuntimeError()
    #     #use prefab to install components required to get pdf generation to work


    def test(self):
        '''
        js_shell 'j.data.markdown.test()'
        '''
        from .tests.test1 import test
        test()
        from .tests.test2 import test
        test()
        from .tests.test3 import test
        test()
        from .tests.test4 import test
        test()
        from .tests.test5 import test
        test()

