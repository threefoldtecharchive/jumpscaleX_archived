from Jumpscale import j
import struct
import redis
import time

r = j.clients.redis.core

pipe = r.pipeline()

nr = 100000


def getmemusage():
    d = r.info()
    return d["used_memory"]


def llist(key="this:is:a:test"):
    r.delete(key)
    mem_pre = getmemusage()
    for i in range(nr):
        pipe.lpush(key, struct.pack("<I", i))

    responses = pipe.execute()

    time.sleep(0.5)

    mem_post = getmemusage()
    mem_used_1k = int((mem_post - mem_pre) / (nr / 1000))

    print("MEM USED PER 1K ITEMS LLIST(%s): %s (bytes)" % (key, mem_used_1k))

    r.delete(key)


def string(key="this:is:a:teststring"):
    r.delete(key)
    mem_pre = getmemusage()

    for i in range(nr):
        l = i * 4
        pipe.setrange(key, l, struct.pack("<I", i))

    responses = pipe.execute()

    time.sleep(0.5)

    mem_post = getmemusage()
    mem_used_1k = int((mem_post - mem_pre) / (nr / 1000))

    r.delete(key)

    print("MEM USED PER 1K ITEMS STRING(%s): %s (bytes)" % (key, mem_used_1k))


def sset(key="this:is:a:sset"):
    r.delete(key)
    mem_pre = getmemusage()

    for i in range(nr):
        pipe.sadd(key, struct.pack("<I", i))

    responses = pipe.execute()

    time.sleep(0.5)

    mem_post = getmemusage()
    mem_used_1k = int((mem_post - mem_pre) / (nr / 1000))

    r.delete(key)

    print("MEM USED PER 1K ITEMS SSET(%s): %s (bytes)" % (key, mem_used_1k))


llist()
# llist("a")
string()
sset()


conclusions = """
storing a string in redis seems to be very large size, no idea why that is
sets are using a lot of memory

size of the key does not make difference in memory usage

"""

print(conclusions)
