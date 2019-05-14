from Jumpscale import j


class LoggerClient(j.application.JSBaseConfigClass):
    """
    is an ssh client
    """

    _SCHEMATEXT = """
        @url = jumpscale.clients.logger.1
        name* = ""
        redis_addr = ""
        redis_port = 22
        redis_secret = ""
        level_min = 0
        filter_processid = "" (LS)
        filter_context= "" (LS) 
        
        """

    def _init(self):
        self._redis_client_ = None

    @property
    def _redis_client(self):
        if self._redis_client_ is None:
            self._redis_client_ = j.clients.redis.get(
                ipaddr=self.redis_addr, port=self.redis_port, password=self.redis_secret
            )

        return self._redis_client_

    def tail(self):
        """
        follow everything coming in in relation to the config mgmt done
        :return:
        """

        j.shell()
