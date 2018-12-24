from Jumpscale import j




class BuilderLibffi(j.builder.system._BaseClass):

    def _init(self):
        self.BUILDDIRL = j.core.tools.text_replace("{DIR_VAR}/build/libffi")
        self.CODEDIRL = j.core.tools.text_replace("{DIR_VAR}/build/code/libffi")

    def reset(self):
        base.reset(self)
        j.sal.fs.remove(self.BUILDDIRL)
        j.sal.fs.remove(self.CODEDIRL)

    def build(self, reset=False):
        """
        js_shell 'j.builder.lib.libffi.build(reset=True)'
        """
        if reset:
            self.reset()

        if self.doneGet("build") and not reset:
            return

        j.builder.system.package.mdupdate()
        j.builder.core.dir_ensure(self.BUILDDIRL)
        if not j.builder.core.isMac:
            j.builder.tools.package_install('dh-autoreconf')
        url = "https://github.com/libffi/libffi.git"
        j.clients.git.pullGitRepo(url, reset=False,dest=self.CODEDIRL, ssh=False)

        if not self.doneGet("compile") or reset:
            C = """
            set -ex
            mkdir -p {DIR_VAR}/build/
            cd {CODEDIRL}
            ./autogen.sh
            ./configure  --prefix={DIR_VAR}/build/ --disable-docs
            make
            make install
            """
            j.sal.fs.writeFile("%s/mycompile_all.sh" % self.CODEDIRL, j.core.tools.text_replace(C))
            self._logger.info("compile libffi")
            self._logger.debug(C)
            j.sal.process.execute("sh %s/mycompile_all.sh" % self.CODEDIRL)            
            self.doneSet("compile")
            self._logger.info("BUILD DONE")
        else:
            self._logger.info("NO NEED TO BUILD")

        self._logger.info("BUILD COMPLETED OK")
        self.doneSet("build")
