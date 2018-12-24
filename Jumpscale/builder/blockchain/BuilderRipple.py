from Jumpscale import j




class BuilderRipple(j.builder.system._BaseClass):
    NAME = "rippled"

    def build(self, reset=False):
        """Get/Build the binaries of ripple
        Keyword Arguments:
            reset {bool} -- reset the build process (default: {False})
        """

        if self._done_get('build') and reset is False:
            return
        
        # rfer to: https://ripple.com/build/rippled-setup/#installing-rippled
    
        j.builder.tools.package_install(['yum-utils', 'alien'])
        cmds = """
        rpm -Uvh https://mirrors.ripple.com/ripple-repo-el7.rpm
        yumdownloader --enablerepo=ripple-stable --releasever=el7 rippled
        rpm --import https://mirrors.ripple.com/rpm/RPM-GPG-KEY-ripple-release && rpm -K rippled*.rpm
        alien -i --scripts rippled*.rpm && rm rippled*.rpm

        """
        j.sal.process.execute(cmds)

        self._done_set('build')

    def install(self, reset=False):
        if self._done_get('install') and reset is False:
            return

        cmds = """
        cp /opt/ripple/bin/rippled {DIR_BIN}/
        """
        j.sal.process.execute(cmds)

        self._done_set('install')
