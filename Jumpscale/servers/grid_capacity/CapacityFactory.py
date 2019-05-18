import requests
import os

from Jumpscale import j

from .CapacityServer import CapacityServer

JSConfigBase = j.application.JSFactoryBaseClass


class CapacityFactory(JSConfigBase):
    def __init__(self):
        self.__jslocation__ = "j.servers.capacity"
        JSConfigBase.__init__(self, CapacityServer)

    def start(self, instance="main", background=False):
        server = self.get(instance, interactive=False)

        if background:
            cmd = "js_shell 'j.servers.capacity.start(instance=\"%s\")'" % (instance)  # IGNORELOCATION
            j.tools.tmux.execute(
                cmd, session="capacity_server", window=instance, pane="main", session_reset=False, window_reset=True
            )
            res = j.sal.nettools.waitConnectionTest("localhost", int(server.config.data["port"]), timeoutTotal=1000)
            if res == False:
                raise RuntimeError("Could not start capacity server on port:%s" % int(server.config.data["port"]))
        else:
            server.start()
