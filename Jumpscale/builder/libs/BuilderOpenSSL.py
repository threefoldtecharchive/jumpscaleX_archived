from Jumpscale import j

JSBASE = j.builder.system._BaseClass


class BuilderOpenSSL(j.builder.system._BaseClass):


    def _init(self):
        self._logger_enable()
        self.BUILDDIRL = j.core.tools.text_replace("{DIR_VAR}/build/openssl")
        self.CODEDIRL = j.core.tools.text_replace("{DIR_VAR}/build/code/openssl")

    def install(self):
        raise RuntimeError("implement")

    def reset(self):
        j.sal.fs.remove(self.BUILDDIRL)
        j.sal.fs.remove(self.CODEDIRL)


    def build(self, reset=False):
        """
        js_shell 'j.builder.libs..openssl.build()'
        """

        if self._done_check("build") and not reset:
            return
        j.builder.buildenv.install()
        url = "https://github.com/openssl/openssl.git"
        j.clients.git.pullGitRepo(url, branch="OpenSSL_1_1_0-stable",dest=self.CODEDIRL, reset=False, ssh=False)

        if not self._done_get("compile") or reset:
            C = """
            set -ex
            mkdir -p {BUILDDIRL}
            cd {CODEDIRL}
            ./config
            ./Configure $target shared enable-ec_nistp_64_gcc_128 no-ssl2 no-ssl3 no-comp --openssldir={BUILDDIRL} --prefix={BUILDDIRL}
            make depend
            make install
            rm -rf {BUILDDIRL}/share
            rm -rf {BUILDDIRL}/build/private
            echo "**BUILD DONE**"
            """
            if j.core.platformtype.myplatform.isMac:
                C = C.replace("$target", "darwin64-x86_64-cc")
            else:
                C = C.replace("$target", "linux-generic64")
            args={}
            args["BUILDDIRL"]=self.BUILDDIRL
            args["CODEDIRL"]=self.CODEDIRL
            C = j.core.tools.text_replace(C,args=args)

            j.sal.fs.writeFile("%s/mycompile_all.sh" % self.CODEDIRL, j.core.tools.text_replace(C))
            self._log_info("compile openssl")
            self._log_debug(C)
            j.sal.process.execute("sh %s/mycompile_all.sh" % self.CODEDIRL)
            self._done_set("compile")
            self._log_info("BUILD DONE")
        else:
            self._log_info("NO NEED TO BUILD")

        self._log_info("BUILD COMPLETED OK")
        self._done_set("build")


    def test(self, build=False):
        """
        js_shell 'j.builder.buildenv(build=True)'
        """
        if build:
            self.build()

        raise RuntimeError("implement")

        print("TEST OK")
