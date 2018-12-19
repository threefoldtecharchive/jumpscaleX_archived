
from Jumpscale import j
JSBASE = j.application.JSBaseClass


class Tutorial(JSBASE):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.tutorials.base"
        JSBASE.__init__(self)


    def cache(self):
        """
        js_shell 'j.tutorials.base.cache()'

        video link:
        https://drive.google.com/open?id=17psosz8ZArs2JwvCIoYA_r06122SpOE-

        :return: result the name given

        """
        assert self._example_run("tutorials/cache/example",name="aname") == "aname"
        self._example_run("tutorials/cache/example_class")


    def baseclass(self):
        """
        js_shell 'j.tutorials.base.baseclass()'

        video link:


        """
        self._example_run("tutorials/baseclass/example",obj_key="dothis",name="aname") == "aname"

