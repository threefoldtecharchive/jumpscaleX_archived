from Jumpscale import j


JSConfigClient = j.application.JSBaseConfigClass

class SonicClient(JSConfigClient):
    """
    Sonic server client
    usage example:-

    cl = j.clients.sonic.get("ingest_client", host="XXXXX", port=XXXX, password="XXX", mode="ingest")
    with cl.client as ingest_client:
      ingest_client.query("collection", "bucket", "object", "text")

    cl = j.clients.sonic.get("search_client", host="XXXXX", port=XXXX, password="XXX", mode="search")
    with cl.client as search_client:
      search_client.query("collection", "bucket", "key")

    """

    _SCHEMATEXT = """
        @url =  jumpscale.sonic.client
        name* = "" (S)
        host = "" (S)
        port = 1491 (I)
        password = "" (S)
        mode = "search" (S)
        """
    def _init(self):
        self.count = self._client_ingest.count
        self.query = self._client_search.query

    @property
    def _client_search(self):
        try:
            from sonic import SearchClient, IngestClient
        except ImportError:
            j.builder.runtimes.python.pip_package_install("sonic-client")
            from sonic import SearchClient, IngestClient

        return SearchClient(host=self.host, port=self.port, password=self.password)

    @property
    def _client_ingest(self):
        try:
            from sonic import SearchClient, IngestClient
        except ImportError:
            j.builder.runtimes.python.pip_package_install("sonic-client")
            from sonic import SearchClient, IngestClient

        return IngestClient(host=self.host, port=self.port, password=self.password)


    # def __enter__(self):
    #     return self.client_search.__enter__()
    #     return self.client_search.__enter__()
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.client.__exit__()
