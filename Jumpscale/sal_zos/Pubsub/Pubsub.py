import asyncio
import json
import ssl
import sys
import time
import uuid

import aioredis


class Response():

    def __init__(self, client, id):
        self._client = client
        self._id = id
        self._queue = 'result:{}'.format(id)

    async def exists(self):
        r = self._client._redis
        flag = '{}:flag'.format(self._queue)
        key_exists = await r.exists(flag)
        return bool(key_exists)

    async def get(self, timeout=None):
        if timeout is None:
            timeout = self._client.timeout
        r = self._client._redis
        start = time.time()
        maxwait = timeout
        while maxwait > 0:
            job_exists = await self.exists()
            if not job_exists:
                raise RuntimeError("Job not found: %s" % self.id)
            v = await r.brpoplpush(self._queue, self._queue, min(maxwait, 10))
            if v is not None:
                return json.loads(v.decode())
            self._logger.debug('%s still waiting (%ss)', self._id, int(time.time() - start))
            maxwait -= 10
        raise TimeoutError()


class Pubsub():

    def __init__(self, loop, host, port=6379, password="", db=0, ctx=None, timeout=None, testConnectionAttempts=3, callback=None):

        socket_timeout = (timeout + 5) if timeout else 15

        self.testConnectionAttempts = testConnectionAttempts

        self._redis = None
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        if ctx is None:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        self.ssl = ctx
        self.timeout = socket_timeout
        self.loop = loop

        async def default_callback(job_id, level, line, meta):
            w = sys.stdout if level == 1 else sys.stderr
            w.write(line)
            w.write('\n')

        self.callback = callback or default_callback
        if not callable(self.callback):
            raise Exception('callback must be callable')

    async def get(self):
        if self._redis is not None:
            return self._redis

        self._redis = await aioredis.create_redis((self.host, self.port),
                                                  loop=self.loop,
                                                  password=self.password,
                                                  db=self.db,
                                                  ssl=self.ssl,
                                                  timeout=self.timeout)
        return self._redis

    async def global_stream(self, queue, timeout=120):
        if self._redis.connection.closed:
            self._redis = await self.get()

        data = await asyncio.wait_for(self._redis.blpop(queue, timeout=timeout), timeout=timeout)

        if data is None:
            return

        _, body = data
        payload = json.loads(body.decode())
        message = payload['message']
        line = message['message']
        meta = message['meta']
        job_id = payload['command']
        await self.callback(job_id, meta >> 16, line, meta & 0xff)

    async def raw(self, command, arguments, queue=None, max_time=None, stream=False, tags=None, id=None):
        if not id:
            id = str(uuid.uuid4())

        payload = {
            'id': id,
            'command': command,
            'arguments': arguments,
            'queue': queue,
            'max_time': max_time,
            'stream': stream,
            'tags': tags,
        }

        self._redis = await self.get()
        flag = 'result:{}:flag'.format(id)

        await self._redis.rpush('core:default', json.dumps(payload))
        if await self._redis.brpoplpush(flag, flag, 10) is None:
            raise TimeoutError('failed to queue job {}'.format(id))
        self._logger.debug('%s >> g8core.%s(%s)', id, command, ', '.join(("%s=%s" % (k, v) for k, v in arguments.items())))

        return Response(self, id)

    async def sync(self, command, args):
        response = await self.raw(command, args)
        result = await response.get()
        if result["state"] != 'SUCCESS':
            raise RuntimeError('invalid response: %s' % result["state"])

        return json.loads(result["data"])

    async def ping(self):
        response = await self.sync('core.ping', {})
        return response

    async def subscribe(self, queue=None):
        response = await self.sync('logger.subscribe', {'queue': queue})
        return response

