from Jumpscale import j
import os
import fnmatch
from pathlib import Path
from Jumpscale.core.generator.JSGenerator import *
from .FixerReplace import FixerReplacer

# ACTIONS
## R = Replace
## RI = Replace case insensitive

JSBASE = j.application.JSBaseClass


class Licenser(j.application.JSBaseClass):

    __jslocation__ = "j.tools.licenser"

    def __init__(self):
        JSBASE.__init__(self)
        self.replacer = FixerReplacer()

    def do(self, path=None, write=False):
        """
        kosmos 'j.tools.licenser.do(write=True)'
        kosmos 'j.tools.licenser.do()'
        :param path:
        :param write:
        :return:
        """
        if not path:
            self.do("/sandbox/code/github/threefoldtech/jumpscaleX", write=write)
            self.do("/sandbox/code/github/threefoldtech/digitalmeX", write=write)
        else:
            for path2 in j.sal.fs.listFilesInDir(path, filter=".gpl3", recursive=True):
                path3 = j.sal.fs.getDirName(path2)
                self.replacer.dir_process(path=path3, write=write)
