
import sys
from Jumpscale import j

class Doc(j.application.JSBaseClass):


    _SCHEMATEXT = """
        @url = jumpscale.docs.docsite.1
        name* = ""
        links = (LO) !jumpscale.docs.link.1
        content = "" (S)
        
        @url = jumpscale.docs.link.1
        name* = ""
        url = (S)
        state = "init,ok,dead" (E)        

        @url = jumpscale.docs.image.1
        name* = ""
        url = (S)
        state = "init,ok,dead" (E)        

        @url = jumpscale.docs.link.1
        name* = ""
        url = (S)
        state = "init,ok,dead" (E)

        """

    def _init(self):
        pass
