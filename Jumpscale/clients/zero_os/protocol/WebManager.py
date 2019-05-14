from . import typchk
from Jumpscale import j


class WebManager:

    _download_chk = typchk.Checker({"url": str, "destination": str})

    def __init__(self, client):
        self._client = client

    def download(self, url, destination):
        """
        download a file from the url and write it to the destination

        parent directory of destination MUST exists for this method to work
        """
        args = {"url": url, "destination": destination}
        self._download_chk.check(args)

        return self._client.raw("web.download", args)
