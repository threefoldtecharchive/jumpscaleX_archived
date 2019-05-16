from Jumpscale import j


class Config:
    def __init__(self, client):
        self._client = client

    def get(self):
        """
        Get the config of g8os
        """
        return self._client.json("config.get", {})
