import logging


class JSLogger(logging.Logger):
    """
    python default logging mechanism

    to raise errors do not use the logger use

    raise j.exceptions....

    """

    def __init__(self, name, factory):
        super(JSLogger, self).__init__(name)
        self.level = 10         #https://docs.python.org/3/library/logging.html#levels  10 is debug
        self.DEFAULT = False
        self.factory = factory
        self._j = factory._j



    def stdout(self,msg,context="",cat=""):
        print(msg)
        from Jumpscale import j
        j.shell()
        w
        self.debug(msg)
