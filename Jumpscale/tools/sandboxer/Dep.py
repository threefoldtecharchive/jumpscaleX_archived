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
        # don't copy self
        if dest == self.path:
            return

        if not j.sal.fs.getFileExtension(dest):
            # dest is a directory
            dest = j.sal.fs.joinPaths(dest, self.name)

        if not j.sal.fs.exists(dest):
            j.sal.fs.copyFile(self.path, dest, createDirIfNeeded=True)

    def __str__(self):
        return "Dep(name='%s', path='%s')" % (self.name, self.path)

    __repr__ = __str__
