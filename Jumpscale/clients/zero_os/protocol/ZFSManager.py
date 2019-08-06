from . import typchk
from Jumpscale import j
import io
import yaml
import re


class ZFSManager:
    PATH = "/var/cache/router.yaml"

    def __init__(self, client):
        self._client = client

    @property
    def config(self):
        """
        Get/Set configuration of the local routing table in one go
        This will fully override the zfs routing table on the host.

        :note: Changes to the routing table will only affect next zero-fs processes
               and will not change the active ones dymaically. Only new containers
               and VMs will get affected by this routing table

        :param table:
           A dict similar to what is returned by `config` it has 3 sections
            - pools
            - lookup
            - cache

            Both lookup, and cache are just ordered list of pool names defined under pools.
            A pool is a dict of rules, where the key is the hash range rule, and value is the destination
            a valid hash range is of the form XX[:YY] where XX is a hash prefix, the YY is optional prefix
            if provided the hash that fallin the the prefix range XX YY will be matched. Destination must
            be a valid url, currently only supported schemes are 'zdb', 'redis', and 'ardb'

            example:
            {
                'pools': {
                    'local': {
                        '00:FF': 'redis://192.168.1.2:6379'
                    }
                }
                'lookup': [
                    'local'
                ],
                'cache': [
                    'local'
                ]
            }
        """

        if not self._client.filesystem.exists(self.PATH):
            return None

        buf = io.BytesIO()
        self._client.filesystem.download(self.PATH, buf)
        buf.seek(0)
        return yaml.load(buf)

    def _valid_hash_range(self, hr):
        m = re.match(r"^([0-9a-fA-F]+)(?::([0-9a-fA-F]+))$", hr)
        if m is None:
            raise j.exceptions.Value('invalid hash range "%s"' % hr)

        start = m.group(1)
        end = m.group(2)

        if end is not None and len(start) != len(end):
            raise j.exceptions.Value("invalid hash range start and end of different length")

    def _valid_dest(self, dest):
        url = urllib.parse.urlparse(dest)
        if url.scheme not in ["ardb", "zdb", "redis"]:
            raise j.exceptions.Value('invalid destination address "%s" only zdb, redis and ardb are supported' % dest)

    @config.setter
    def config(self, table):

        for name, pool in table["pools"].items():
            for hash_range, dest in pool.items():
                self._valid_hash_range(hash_range)
                self._valid_dest(dest)

        for lookup in table["lookup"]:
            if lookup not in table["pools"]:
                raise j.exceptions.Value("unknown pool name '%s' in lookup" % lookup)

        for cache in table.get("cache", []):
            if cache not in table["pools"]:
                raise j.exceptions.Value("unknown pool name '%s' in lookup" % lookup)

        final = {"pools": table["pools"], "lookup": table["lookup"], "cache": table.get("cache", [])}
        buf = io.BytesIO(yaml.dump(final).encode())
        self._client.filesystem.upload(self.PATH, buf)

    def purge(self):
        """
        Remove routing table, this will cause zos to only depend on the routing table
        provided by the flist, no local pools or caching will happen.
        """
        self._client.filesystem.remove(self.PATH)

    def set_cache(self, destination):
        """
        A simple method to set local cache redis, or zdb in one go. It overrides
        any entries in the routing table.
        """

        self.config = {"pools": {"local": {"00:FF": destination}}, "lookup": ["local"], "cache": ["local"]}
