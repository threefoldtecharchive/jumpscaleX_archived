
import sys
from Jumpscale import j

class Navigation(j.application.JSBaseClass):
    """
    is the navigation menu
    """

    _SCHEMATEXT = """
        @url = jumpscale.docs.navigation.1
        name* = ""
        links = (LO) !jumpscale.docs.navigation.1
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
