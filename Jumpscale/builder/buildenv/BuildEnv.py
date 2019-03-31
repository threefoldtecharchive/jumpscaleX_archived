from Jumpscale import j


class BuildEnv(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.buildenv"

    def install(self, reset=False, upgrade=True):

        if self._done_check("install", reset):
            return

        self.upgrade()

        if not self._done_check("fixlocale", reset):
            j.tools.bash.local.locale_check()
            self._done_set("fixlocale")

        # out = ""
        # make sure all dirs exist
        # for key, item in j.builder.tools.dir_paths.items():
        #     out += "mkdir -p %s\n" % item
        # j.sal.process.execute(out)

        j.builder.system.package.mdupdate()

        # if not j.core.platformtype.myplatform.isMac and not j.builder.tools.isCygwin:
        #     j.builder.system.package.ensure("fuse")

        if j.builder.tools.isArch:
            # is for wireless auto start capability
            j.builder.system.package.ensure("wpa_actiond,redis-server")

        if j.core.platformtype.myplatform.isMac:
            C = ""
        else:
            C = "sudo net-tools python3 python3-distutils python3-psutil"

        C += " openssl wget curl git mc tmux rsync"
        j.builder.system.package.ensure(C)

        # j.builder.sandbox.profileJS.path_add("{DIR_BIN}")
        # j.builder.sandbox.profileJS.save()

        if upgrade:
            self.upgrade(reset=reset, update=False)

        self._done_set("install")

    def development(self, reset=False, python=False):
        """
        install all components required for building (compiling)

        to use e.g.
            js_shell 'j.builder.buildenv.development()'

        """

        C = """
        autoconf        
        gcc
        make        
        autoconf
        libtool
        pkg-config
        curl
        """
        C = j.core.text.strip(C)

        if j.core.platformtype.myplatform.isMac:

            if not self._done_get("xcode_install"):
                j.sal.process.execute("xcode-select --install", die=False, showout=True)
                cmd = "sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /"
                j.sal.process.execute(cmd, die=False, showout=True)
                self._done_set("xcode_install")

            C += "libffi "
            C += "automake "
            C += "pcre "
            C += "xz "
            C += "openssl "
            C += "zlib "
        else:
            C += "libffi-dev "
            C += "build-essential "
            C += "libsqlite3-dev "
            C += "libpq-dev "
            if python:
                C += "python3-dev "

        self.install()
        if self._done_check("development", reset):
            return
        j.builder.system.package.ensure(C)
        self._done_set("development")

    def upgrade(self, reset=False, update=True):
        if self._done_check("upgrade", reset):
            return
        if update:
            j.builder.system.package.mdupdate(reset=reset)
        j.builder.system.package.upgrade(reset=reset)
        j.builder.system.package.clean()

        self._done_set("upgrade")
