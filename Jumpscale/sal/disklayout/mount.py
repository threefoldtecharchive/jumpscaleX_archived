from Jumpscale import j

JSBASE = j.application.JSBaseClass


class MountError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class Mount(j.application.JSBaseClass):
    def __init__(self, device, path=None, options="", executor=None):
        JSBASE.__init__(self)
        self._device = device
        self._path = path
        self._autoClean = False
        if self._path is None:
            self._path = j.tools.path.get("/tmp").joinpath(j.data.idgenerator.generateXCharID(8))
            self._autoClean = True
        self._options = options
        self._executor = executor or j.tools.executorLocal

    @property
    def _mount(self):
        return "mount {options} {device} {path}".format(
            options="-o " + self._options if self._options else "", device=self._device, path=self._path
        )

    @property
    def _umount(self):
        return "umount {path}".format(path=self._path)

    @property
    def path(self):
        return self._path

    def __enter__(self):
        return self.mount()

    def __exit__(self, type, value, traceback):
        return self.umount()

    def mount(self):
        """
        Mount partition
        """
        try:
            self._executor.prefab.core.dir_ensure(self.path)
            rc, out, err = self._executor.execute(self._mount, showout=False)
            if err != "":
                raise MountError(err)
        except Exception as e:
            raise MountError(e)
        return self

    def umount(self):
        """
        Umount partition
        """
        try:
            rc, out, err = self._executor.execute(self._umount, showout=False)
            if err != "":
                raise MountError(err)
            if self._autoClean:
                self._executor.prefab.core.dir_remove(self.path)
        except Exception as e:
            raise MountError(e)
        return self
