from Jumpscale import j
from Jumpscale.data.bcdb.RedisServer import RedisServer
from collections import deque


# base_redis = j.servers.redis

class RedisLoggingServer(RedisServer):
    __jslocation__ = 'j.servers.redis_logger'

    def _init(self, addr="localhost",port=6379,secret=""):
        self._sig_handler = []
        self.host = addr
        self.port = port  # 1 port higher than the std port
        self.secret = secret
        self.ssl = False
        self.redis_server = None
        self.init()
        self.logger = Logger()

    def _handle_redis(self, socket, address, parser, response):
        """
        overrrides RedisServer._handle_redis, this method is responsible for handling the commands
        """

        self._logger.info('connection from {}'.format(address))
        socket.namespace = "system"

        while True:
            request = parser.read_request()

            self._logger.debug("%s:%s" % (socket.namespace, request))

            if request is None:
                self._logger.debug("connection lost or tcp test")
                break

            if not request:  # empty list request
                self._logger.debug("EMPTYLIST")
                continue

            cmd = request[0]
            redis_cmd = cmd.decode("utf-8").lower()

            if redis_cmd == "command":
                response.encode("OK")
                continue

            elif redis_cmd == "ping":
                response.encode("PONG")
                continue

            elif redis_cmd == "log":
                args = request[1:] if len(request) > 1 else []
                args = [x.decode() for x in args]
                self.log(response, *args)
                continue

            else:
                response.error("Unknow command, this redis server is just for logging\n"
                               "it should be used as following:\n"
                               "LOG $LOGDEST 0 $STDOUTLINE\n"
                               "LOG $LOGDEST 1 $STDERRLINE")

    def log(self, response, *args):
        if len(args) == 1:
            response.encode(self.logger.list(args[0]))
            return
        if len(args) == 3:
            [dest, level, content] = args
            self.logger.log(dest, level, content)
            response.encode("OK")
        else:
            response.error("Invalid arguments for log {}, {}".format(args, len(args)))
            return

    def test(self):
        self.logger.test()


class Logger:
    """
    Object to handle and store all logs for the logger
    the logs are stored in the following structure
    {"dest$level": deque("content")}
    example
    {"myapp$0": deque(["out1", "out2"]),
     "myapp$1": deque(["err1", "err2"])}
    """
    def __init__(self, limit=1000):
        self.limit = limit
        self.logs = {}

    def log(self, dest, level, content):
        """
        insert a new log
        :param dest: the logging context
        :param level: the level of the log (0: std_out, 1:std_err)
        :param content: the content
        """
        key = "{}${}".format(dest, level)
        prev_logs = self.logs.get(key, deque(maxlen=self.limit))
        prev_logs.append(content)
        self.logs[key] = prev_logs

    def list(self, dest):
        """
        lists all logs for a givin context
        :param dest: the logging context
        :return: dict of "std_err" and "std_out"
        """
        out_key = "{}${}".format(dest, 0)
        err_key = "{}${}".format(dest, 1)
        return {"std_err": list(self.logs.get(err_key, [])), "std_out": list(self.logs.get(out_key, []))}

    def test(self):
        for i in range(10000):
            self.log("test", 0, "out_{}".format(i))
            self.log("test", 1, "err_{}".format(i))

        out_res = ["out_{}".format(i) for i in range(9000, 10000)]
        err_res = ["err_{}".format(i) for i in range(9000, 10000)]

        data = self.list("test")
        assert data["std_out"] == out_res
        assert data["std_err"] == err_res

        print("**DONE**")
