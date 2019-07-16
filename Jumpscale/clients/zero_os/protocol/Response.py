import textwrap
import json
import time
import logging
import sys

from Jumpscale import j

logger = logging.getLogger("zoosprotocol")


class JobNotFoundError(Exception):
    pass


class ResultError(RuntimeError):
    def __init__(self, msg, code=0):
        super().__init__(msg)

        self._message = msg
        self._code = code

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message


class Return:
    def __init__(self, payload):
        self._payload = payload

    @property
    def payload(self):
        """
        Raw return object data
        :return: dict
        """
        return self._payload

    @property
    def id(self):
        """
        Job ID
        :return: string
        """
        return self._payload["id"]

    @property
    def data(self):
        """
        Data returned by the process. Only available if process
        output data with the correct core level

        For example, if a job returns a json object the self.level will be 20 and the data will contain the serialized
        json object, other levels exists for yaml, toml, etc... it really depends on the running job
        return: python primitive (str, number, dict or array)
        """
        return self._payload["data"]

    @property
    def level(self):
        """
        Data message level (if any)
        """
        return self._payload["level"]

    @property
    def starttime(self):
        """
        Starttime as a timestamp
        """
        return self._payload["starttime"] / 1000

    @property
    def time(self):
        """
        Execution time in millisecond
        """
        return self._payload["time"]

    @property
    def state(self):
        """
        Exit state
        :return: str one of [SUCCESS, ERROR, KILLED, TIMEOUT, UNKNOWN_CMD, DUPLICATE_ID]
        """
        return self._payload["state"]

    @property
    def stdout(self):
        """
        The job stdout
        :return: string or None
        """
        streams = self._payload.get("streams", None)
        return streams[0] if streams is not None and len(streams) >= 1 else ""

    @property
    def stderr(self):
        """
        The job stderr
        :return: string or None
        """
        streams = self._payload.get("streams", None)
        return streams[1] if streams is not None and len(streams) >= 2 else ""

    @property
    def code(self):
        """
        Exit code of the job, this can be either one of the http codes, of (if the value > 1000)
        is the exit code of the underlaying process
        if code > 1000:
            exit_code = code - 1000

        """
        return self._payload.get("code", 500)

    def __repr__(self):
        return str(self)

    def __str__(self):
        tmpl = """\
        STATE: {code} {state}
        STDOUT:
        {stdout}
        STDERR:
        {stderr}
        DATA:
        {data}
        """

        return textwrap.dedent(tmpl).format(
            code=self.code, state=self.state, stdout=self.stdout, stderr=self.stderr, data=self.data
        )


class Response:
    def __init__(self, client, id):
        self._client = client
        self._id = id
        self._queue = "result:{}".format(id)

    @property
    def id(self):
        """
        Job ID
        :return: string
        """
        return self._id

    @property
    def exists(self):
        """
        Returns true if the job is still running or zero-os still knows about this job ID

        After a job is finished, a job remains on zero-os for max of 5min where you still can read the job result
        after the 5 min is gone, the job result is no more fetchable
        :return: bool
        """
        r = self._client.redis
        flag = "{}:flag".format(self._queue)
        return bool(r.exists(flag))

    @property
    def running(self):
        """
        Returns true if job still in running state
        :return:
        """
        r = self._client.redis
        flag = "{}:flag".format(self._queue)
        return r.ttl(flag) == -1

    def stream(self, callback=None):
        """
        Runtime copy of job messages. This required the 'stream` flag to be set to True otherwise it will
        not be able to copy any output, while it will block until the process exits.

        :note: This function will block until it reaches end of stream or the process is no longer running.

        :param callback: callback method that will get called for each received message
                         callback accepts 3 arguments
                         - level int: the log message levels, refer to the docs for available levels
                                      and their meanings
                         - message str: the actual output message
                         - flags int: flags associated with this message
                                      - 0x2 means EOF with success exit status
                                      - 0x4 means EOF with error

                                      for example (eof = flag & 0x6) eof will be true for last message u will ever
                                      receive on this callback.

                         Note: if callback is none, a default callback will be used that prints output on stdout/stderr
                         based on level.
        :return: the number of message received during the streaming
        """
        if callback is None:
            callback = Response.__default

        if not callable(callback):
            raise Exception("callback must be callable")

        queue = "stream:%s" % self.id
        r = self._client.redis

        count = 0
        while True:
            data = r.blpop(queue, 10)
            if data is None:
                if not self.running:
                    break
                continue
            _, body = data
            payload = json.loads(body.decode())
            message = payload["message"]
            line = message["message"]
            meta = message["meta"]
            callback(meta >> 16, line, meta & 0xFF)
            count += 1

            if meta & 0x6 != 0:
                break

        return count

    @staticmethod
    def __default(level, line, meta):
        w = sys.stdout if level == 1 else sys.stderr
        w.write(line)

    def get(self, timeout=None):
        """
        Waits for a job to finish (max of given timeout seconds) and return job results. When a job exits get() will
        keep returning the same result until zero-os doesn't remember the job anymore (self.exists == False)

        :notes: the timeout here is a client side timeout, it's different than the timeout given to the job on start
        (like in system method) witch will cause the job to be killed if it exceeded this timeout.

        :param timeout: max time to wait for the job to finish in seconds
        :return: Return object
        """
        if timeout is None:
            timeout = self._client.timeout
        r = self._client.redis
        start = time.time()
        maxwait = timeout
        while maxwait > 0:
            if not self.exists:
                raise JobNotFoundError(self.id)
            try:
                v = r.brpoplpush(self._queue, self._queue, min(maxwait, 10))
                if not v is None:
                    payload = json.loads(v.decode())
                    r = Return(payload)
                    return r
            except TimeoutError:
                pass
            logger.debug("%s still waiting (%ss)", self._id, int(time.time() - start))
            maxwait -= 10
        raise TimeoutError()


class JSONResponse(Response):
    def __init__(self, response):
        super().__init__(response._client, response.id)

    def get(self, timeout=None):
        """
        Get response as json, will fail if the job doesn't return a valid json response

        :param timeout: client side timeout in seconds
        :return: int
        """
        result = super().get(timeout)
        if result.state != "SUCCESS":
            raise ResultError(result.data, result.code)
        if result.level != 20:
            raise ResultError("not a json response: %d" % result.level, 406)

        return json.loads(result.data)
