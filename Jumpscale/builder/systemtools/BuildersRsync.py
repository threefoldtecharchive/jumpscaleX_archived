from Jumpscale import j


class BuilderRsync()
    Rsync(j.builder.system._BaseClass):


    def __init(self):
        self._logger_enable()
        self.BUILDDIRL = j.core.tools.text_replace("{DIR_VAR}/build/rsync/")
        self.VERSION = 'rsync-3.1.2'

    def reset(self):
        j.sal.fs.remove(self.BUILDDIRL)
        self.doneDelete("build")

    def build(self, reset=False, install=True):
        """
        """

        if reset:
            self.reset()

        if self._done_get("build") and not reset:
            return

        j.core.tools.dir_ensure(self.BUILDDIRL)

        j.builder.system.package.ensure("gcc")
        j.builder.system.package.ensure("g++")
        j.builder.system.package.ensure('make')

        j.builder.tools.file_download(
            "https://download.samba.org/pub/rsync/src/%s.tar.gz" %
            self.VERSION, to="%s/%s.tar.gz" %
            (self.BUILDDIRL, self.VERSION))

        C = """
        set -xe
        cd {DIR_VAR}/build/
        tar -xf $VERSION.tar.gz
        cd $VERSION
        ./configure
        make
        """
        C = C.replace('{DIR_VAR}/build/', self.BUILDDIRL)
        C = C.replace('$VERSION', self.VERSION)
        j.sal.process.execute(C, profile=True)

        self._done_set("build")
        if install:
            self.install()

    def install(self,build=False):
        if build:
            if not self._done_get("build"):
                self.build(install=False)
            j.builder.sandbox.profileDefault.addPath(j.builder.tools.replace("{DIR_BIN}"))
            j.builder.sandbox.profileDefault.save()
            j.builder.tools.file_copy(
                "%s/%s/rsync" %
                (self.BUILDDIRL,
                self.VERSION),
                '{DIR_BIN}')
        else:
            j.builder.tools.package_install("rsync")

    def configure(self):
        self.install(build=False)

