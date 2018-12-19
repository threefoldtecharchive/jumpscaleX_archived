from Jumpscale import j
import pssh.exceptions

import copy
import unicodedata
import sys

LEVELMAP = {1: 'CRITICAL', 2: 'WARNING', 3: 'INFO', 4: 'DEBUG'}


class BaseJSException(Exception):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        if not j.data.types.int.check(level):
            level=1
        super().__init__(message)
        self.message = message
        self.message_pub = msgpub
        self.level = level
        if level not in LEVELMAP:
            raise RuntimeError("level needs to be 1-4")
        self.cat = cat                      #is a dot notation category, to make simple no more tags
        self.trace_do = False
        self._trace = ""                     #info to find back where it was

    @property
    def trace(self):
        return self._trace

    @property
    def type(self):
        return j.core.text.strip_to_ascii_dense(str(self.__class__))


    @property
    def str_1_line(self):
        """
        1 line representation of error

        """
        msg = ""
        if self.level > 1:
            msg += "level:%s " % self.level
        if self.type != "":
            msg += "type:%s " % self.type
        # if self._tags_add != "":
        #     msg += " %s " % self._tags_add
        return msg.strip()


    def __str__(self):
        if self.cat is not "":
            out = "ERROR: %s ((%s)\n" % (self.message, self.cat)
        else:
            out = "ERROR: %s\n" % (self.message)
        if self._trace is not "":
            j.errorhandler._trace_print(self._trace)
            return ""
        else:
            return out

    __repr__ = __str__



    def trace_print(self):
        j.core.errorhandler._trace_print(self._trace)



class HaltException(BaseJSException):
    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True


class RuntimeError(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True


class Input(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True


class NotImplemented(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True


class BUG(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True


class JSBUG(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True


class OPERATIONS(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = False


class IOError(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True



class NotFound(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True


class Timeout(BaseJSException):

    def __init__(self, message="", level=1, cat="", msgpub=""):
        super().__init__(message=message,level=level,cat=cat,msgpub=msgpub)
        self.trace_do = True

SSHTimeout = pssh.exceptions.Timeout
