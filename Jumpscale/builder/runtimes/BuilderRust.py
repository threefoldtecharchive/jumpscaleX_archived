from Jumpscale import j




class BuilderRust(j.builder.system._BaseClass):
    NAME = 'rust'

    def install(self, reset=False):
        """

        """
        if self._done_get("install") and not reset:
            return

        version = 'rust-nightly-x86_64-unknown-linux-gnu'
        url = 'https://static.rust-lang.org/dist/{}.tar.gz'.format(version)
        dest = '/tmp/rust.tar.gz'
        j.sal.process.execute('curl -o {} {}'.format(dest, url))
        j.sal.process.execute('tar --overwrite -xf {} -C /tmp/'.format(dest))

        # copy file to correct locations.
        j.sal.process.execute(
            'cd /tmp/{version} && ./install.sh --prefix={DIR_BASE}/apps/rust --destdir=={DIR_BASE}/apps/rust'.format(version=version))

        # was profileDefault
        #j.builder.sandbox.profileJS.addPath(j.core.tools.text_replace('{DIR_BASE}/apps/rust/bin'))
        #j.builder.sandbox.profileJS.save()

        self._done_set('install')
