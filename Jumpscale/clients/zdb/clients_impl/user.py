from ..ZDBClientBase import ZDBClientBase



class ZDBClientUserMode(ZDBClientBase):

    def __init__(self, nsname, factory=None, addr="localhost", port=9900, secret="123456", admin_secret=None):
        super().__init__(factory=factory,addr=addr, port=port, mode="user", nsname=nsname, secret=secret)

    def set(self, data, key):
        return self.redis.execute_command("SET", key, data)
