from . import typchk
from Jumpscale import j


class LogManager:
    _level_chk = typchk.Checker({"level": typchk.Enum("CRITICAL", "ERROR", "WARNING", "NOTICE", "INFO", "DEBUG")})

    _subscribe_chk = typchk.Checker({"queue": str, "levels": [int]})

    def __init__(self, client):
        self._client = client

    def set_level(self, level):
        """
        Set the log level of the g8os
        Note: this level is for messages that ends up on screen or on log file

        :param level: the level to be set can be one of ("CRITICAL", "ERROR", "WARNING", "NOTICE", "INFO", "DEBUG")
        """
        args = {"level": level}
        self._level_chk.check(args)

        return self._client.json("logger.set_level", args)

    def reopen(self):
        """
        Reopen log file (rotate)
        """
        return self._client.json("logger.reopen", {})

    def subscribe(self, queue=None, *levels):
        """
        Subscribe to the aggregated log stream. On subscribe a ledis queue will be fed with all running processes
        logs. Always use the returned queue name from this method, even if u specified the queue name to use

        Note: it is legal to subscribe to the same queue, but would be a bad logic if two processes are trying to
        read from the same queue.

        :param queue: Your unique queue name, otherwise, a one will get generated for your
        :param levels:
        :return: queue name to pull from
        """
        args = {"queue": queue, "levels": list(levels)}

        self._subscribe_chk.check(args)

        return self._client.json("logger.subscribe", args)

    def unsubscribe(self, queue):
        """
        Unsubscribe will kill the queue on node zero, further reading on that queue will just get what has been
        queued before calling unsubscribe, after that reading on that queue will not return anything.

        :param queue: Queue name as returned from self.subscribe
        :return:
        """
        return self._client.json("logger.unsubscribe", {"queue": queue})
