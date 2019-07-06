from Jumpscale import j


class Test(j.application.JSBaseClass):
    def _init(self):
        self.r = j.clients.redis.core
        self._ns = "tutorial"
        self.scripts = {}

    def register_script(self, name, nrkeys=0):

        lua_path = "%s/%s.lua" % (self._dirpath, name)

        if not j.sal.fs.exists(lua_path):
            raise RuntimeError("cannot find:%s" % lua_path)

        name2 = "%s_%s" % (self._ns, name)

        self.scripts[name] = self.r.storedprocedure_register(name2, nrkeys, lua_path)

        return self.scripts[name]

    def execute(self, name, *args):
        name2 = "%s_%s" % (self._ns, name)
        self.r.storedprocedure_execute(name2, *args)

    def debug(self, name, *args):
        """
        to see how to use the debugger see https://redis.io/topics/ldb

        to break put: redis.breakpoint() inside your lua code
        to continue: do 'c'


        :param name: name of the sp to execute
        :param args: args to it
        :return:
        """
        name2 = "%s_%s" % (self._ns, name)
        self.r.storedprocedure_debug(name2, *args)

    def do(self):
        self.register_script("set", 3)
        key = 0  # means not used
        data = b"1234"
        self.debug("set", "nstest", key, data)


t = Test()
t.do()
