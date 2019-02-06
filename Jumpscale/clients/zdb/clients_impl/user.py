from ..ZDBClientBase import ZDBClientBase



class ZDBClientUserMode(ZDBClientBase):

    def set(self, data, key):
        return self.redis.execute_command("SET", key, data)
