from Jumpscale import j
from .JSRunProcess import JSRunProcess

JSBASE = j.application.JSBaseClass


class JSRun(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.servers.jsrun"

        JSBASE.__init__(self)
        self.latest = None
        self.processes = {}
        self._installed = False

    def install(self):
        """
        js_shell 'j.servers.jsrun.install()'

        """
        if self._installed:
            return
        p = j.tools.prefab.local

        if p.core.doneGet("jsrun") is False:

            j.servers.openresty.install()

            p.core.doneSet("jsrun")

        self._installed = True

    def get(self, name, cmd="", path=None, env={}, ports=[], stopcmd="", process_strings=[], reset=False):
        """

        :param name: name of the session
        :param cmd:
        :param path: path to start from
        :param env:
        :param ports:
        :param stopcmd: cmd to execute when to stop, will not die if not succesfull
        :param process_strings: if specified will look for processes which have this as par of name & kill
        :return:
        """
        p = JSRunProcess(
            name=name, cmd=cmd, path=path, env=env, ports=ports, stopcmd=stopcmd, process_strings=process_strings
        )
        if reset:
            p.stop()
        self.processes[name] = p
        return self.processes[name]

    def start(self, name, cmd="", path=None, env={}, ports=[], stopcmd="", process_strings=[], reset=False):
        p = self.get(
            name=name,
            cmd=cmd,
            path=path,
            reset=reset,
            env=env,
            ports=ports,
            stopcmd=stopcmd,
            process_strings=process_strings,
        )
        p.start()
        return p

    def test(self, name="", start=True):
        """
        following will run all tests

        js_shell 'j.servers.web.test()'

        """

        self._test_run(name=name)
