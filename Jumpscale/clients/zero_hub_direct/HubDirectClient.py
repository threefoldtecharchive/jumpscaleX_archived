from Jumpscale import j
from .client import Client
import base64

JSConfigClient = j.application.JSBaseConfigClass


class HubDirectClient(JSConfigClient):
    """
    Communicates directly to the remote storage
    don't use this if you just want to upload or list flists, use j.clients.zhub instead
    """

    _SCHEMATEXT = """
    @url = jumpscale.hubdirect.client
    name* = "" (S)
    base_uri = "https://direct.hub.grid.tf" (S)
    jwt_ = "" (S)
    """

    def _init(self):
        self._api = None

    @property
    def api(self):
        if self._api is None:
            self._api = Client(base_uri=self.config.data["base_uri"])
            self._api.security_schemes.passthrough_client_jwt.set_authorization_header(
                "bearer %s" % self.config.data["jwt_"]
            )
        return self._api

    def exists(self, keys):
        # ensure keys are in bytes
        def is_str(x):
            return isinstance(x, str)

        binary_keys = list(map(str.encode, filter(is_str, keys)))
        # base64 encode the keys
        bencoded = list(map(base64.b64encode, binary_keys))
        # bytes to str
        decoded = list(map(bytes.decode, bencoded))

        return self.api.exists.exists_post(data=decoded)

    def insert(self, keys_data):
        """
        @param keys_data: dictionnary with key=hash value=data
        """
        data = tuple()
        for k, v in keys_data.items():
            # ensure key and value are bytes
            if isinstance(k, str):
                k = k.encode()
            if isinstance(v, str):
                v = v.encode()

            if not k.startswith(b"MTAwMDAw"):
                # b64encode the key if it is not already the case
                b64_k = base64.b64encode(k).decode()
            data += (("files[]", (b64_k, v)),)

        return self.api.insert.insert_put(data=data, content_type="multipart/form-data")
