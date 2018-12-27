import os
# import sys
import atexit
import struct
from collections import namedtuple
import psutil
import traceback
from .JSBase import JSBase
from .JSFactoryBase import JSFactoryBase
from .JSBaseConfig import JSBaseConfig


class DictEditor(object):

    def __init__(self,j,ddict):

        self._j = j

        self._ddict = ddict

    def __getattr__(self, name):
        if name.startswith("_"):
            return self.__dict__[name]
        if name not in self._ddict:
            raise RuntimeError("cannot find name in ")
        return self._ddict[name]

    def __dir__(self):
        m = self.__dict__["_factory"]
        return [item.name for item in m._get_all()]

    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name]=value
            return
        m = self.__dict__["_factory"]
        o=m.get(name=name,die=False)
        j.shell()

    def __str__(self):
        try:
            out = "%s\n%s\n"%(self.__class__.__name__,self.data)
        except:
            out = str(self.__class__)+"\n"
            out+=j.core.text.prefix(" - ", self.data)
        return out

    __repr__ = __str__
