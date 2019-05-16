from Jumpscale import j

JSBASE = j.application.JSBaseClass


class Dep(j.application.JSBaseClass):
    def __init__(self, name, path):
        JSBASE.__init__(self)
        self.name = name
        self.path = path
        try:
            j.sal.fs.isLink(self.path)
        except Exception as e:
            j.shell()
        if j.sal.fs.isLink(self.path):
            link = j.sal.fs.readLink(self.path)
            if j.sal.fs.exists(path=link):
                self.path = link
                return
            else:
                base = j.sal.fs.getDirName(self.path)
                potpath = j.sal.fs.joinPaths(base, link)
                if j.sal.fs.exists(potpath):
                    self.path = potpath
                    return
        else:
            if j.sal.fs.exists(self.path):
                return
        raise j.exceptions.RuntimeError("could not find lib (dep): '%s'" % self.path)

    def copyTo(self, path):
        dest = j.sal.fs.joinPaths(path, self.name)
        dest = dest.replace("//", "/")
        j.sal.fs.createDir(j.sal.fs.getDirName(dest))
        if dest != self.path:  # don't copy to myself
            # self._log_debug("DEPCOPY: %s %s" % (self.path, dest))
            if not j.sal.fs.exists(dest):
                j.sal.fs.copyFile(self.path, dest)

    def __str__(self):
        return "%-40s %s" % (self.name, self.path)

    __repr__ = __str__
