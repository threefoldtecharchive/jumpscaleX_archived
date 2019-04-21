from Jumpscale import j


JSConfigClient = j.application.JSBaseConfigClass

class SonicClient(JSConfigClient):
    """
    Sonic server client
    usage example:-

    cl = j.clients.sonic.get("ingest_client", host="XXXXX", port=XXXX, password="XXX")
    with cl.client as ingest_client:
      ingest_client.push("collection", "bucket", "object", "text")

    cl = j.clients.sonic.get("search_client", host="XXXXX", port=XXXX, password="XXX")
    with cl.client as search_client:
      search_client.query("collection", "bucket", "key")

    """
    _SCHEMATEXT = """
        @url =  jumpscale.sonic.client
        name* = "" (S)
        host = "127.0.0.1" (S)
        port = 1491 (I)
        password = "" (S)
        """
    def _init(self):
        self._cached_client_search = None
        self._cached_client_ingest = None

        self.push = self._client_ingest.push
        self.pop = self._client_ingest.pop
        self.count = self._client_ingest.count
        self.flush = self._client_ingest.flush
        self.flush_collection = self._client_ingest.flush_collection
        self.flush_bucket = self._client_ingest.flush_bucket
        self.flush_object = self._client_ingest.flush_object

        self.query = self._client_search.query
        self.suggest = self._client_search.suggest

    @property
    def _client_search(self):
        try:
            from sonic import SearchClient, IngestClient
        except ImportError:
            j.builder.runtimes.python.pip_package_install("sonic-client")
            from sonic import SearchClient, IngestClient

        if not self._cached_client_search:
            self._cached_client_search = SearchClient(host=self.host, port=self.port, password=self.password)
            self._cached_client_search.connect()
            return self._cached_client_search

    @property
    def _client_ingest(self):
        try:
            from sonic import SearchClient, IngestClient
        except ImportError:
            j.builder.runtimes.python.pip_package_install("sonic-client")
            from sonic import SearchClient, IngestClient

        if not self._cached_client_ingest:
            self._cached_client_ingest = IngestClient(host=self.host, port=self.port, password=self.password)
            self._cached_client_ingest.connect()
            return self._cached_client_ingest
    