from Jumpscale import j


class BuilderCaddyFilemanager(j.builder.system._BaseClass):
    NAME = 'filemanager'
    PLUGINS = ['iyo', 'filemanager']

    def build(self, reset=False):
        """
        build caddy with iyo authentication and filemanager plugins

        :param reset: reset the build process, defaults to False
        :type reset: bool, optional
        """
        j.builder.web.caddy.build(plugins=self.PLUGINS, reset=reset)

    def install(self, reset=False):
        """
        install caddy binary

        :param reset: reset build and installation, defaults to False
        :type reset: bool, optional
        """
        j.builder.web.caddy.install(reset=reset)
