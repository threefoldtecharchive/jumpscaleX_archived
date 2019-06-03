from Jumpscale import j

JSBASE = j.application.JSBaseClass


class Dep(j.application.JSBaseClass):
    def __init__(self, name, path):
        JSBASE.__init__(self)
        self.name = name
        self.path = path

        if not j.sal.fs.exists(self.path):
            raise j.exceptions.RuntimeError("could not find lib (dep): '%s'" % self.path)

    def copyTo(self, dest):
        dest = dest.replace("//", "/")
        j.sal.fs.createDir(j.sal.fs.getDirName(dest))
        if dest != self.path:  # don't copy to myself
            # self._log_debug("DEPCOPY: %s %s" % (self.path, dest))
            if not j.sal.fs.exists(dest):
                j.sal.fs.copyFile(self.path, dest, follow_symlinks=True)

    def __str__(self):
        return "Dep(name='%s', path='%s')" % (self.name, self.path)

    __repr__ = __str__
