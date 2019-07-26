from Jumpscale import j
import time
import json
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict

JSConfigClient = j.application.JSBaseConfigClass


class GedisWebsocketServer(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.gedis.websocket.1
        name* = "default" (S)
        port = 4444
        """

    def _init(self, **kwargs):
        self._server = None
        self._app = None

    @property
    def server(self):
        if not self._server:
            self._server = WebSocketServer(("0.0.0.0", self.port), Resource(OrderedDict([("/", Application)])))
        return self._server

    @property
    def app(self):
        if not self._app:
            self._app = Application
        return self._app

    def start(self, name="websocket"):
        """
        kosmos 'j.servers.gedis_websocket.start()'
        :param manual means the server is run manually using e.g. kosmos 'j.servers.rack.start()'
        """

        self.server.start()

    def test(self):
        self.default.start()
        self.default.stop()


class Application(WebSocketApplication):
    def on_message(self, message):
        print(message)
        if message is None:
            return

        data = json.loads(message)
        commands = data["command"].split(".")
        cl = getattr(self.client_gedis.actors, commands[0])

        for attr in commands[1:]:
            cl = getattr(cl, attr)

        args = data.get("args", {})

        response = cl(**args)

        self.ws.send(j.data.serializers.json.dumps(response))

    def on_close(self, reason):
        print(reason)

    def on_open(self):
        self.client_gedis = j.clients.gedis.get("main", port=8900)
