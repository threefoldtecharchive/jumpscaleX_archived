from Jumpscale import j


class CoreXProcess(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.corex.process
    name* = "" (S)
    corex_name* = "" (S)
    state = "init,ok,error,stopped,stopping" (E)
    pid* = 0
    corex_id* = (S)
    time_start = (T)
    time_refresh = (T)
    time_stop = (T)
    ports = [] (LI)
    cmd = ""
    
    
    """

    def _init(self):
        self.state = "init"
        pass

    def stop(self):
        self.refresh()
        if not self.state in ["init", "stopped", "stopping"]:
            r = self.client._query("/process/stop", params={"id": self.corex_id})
        self.refresh()

    @property
    def logs(self):
        r = self.client._query("/process/logs", params={"id": self.corex_id}, json=False)
        return r

    def start(self, kill=False):

        if kill:
            self.stop()
        else:
            self.refresh()

        if self.state == "error":
            raise RuntimeError("process in error:\n%s" % p)

        if self.state == "ok":
            return

        if self.state == "stopped":

            args = [arg for arg in self.cmd.split(" ")]
            params = {"arg[]": args}
            r = self.client._query("/process/start", params=params)

            self.state = "ok"
            self.pid = r["pid"]
            self.corex_id = r["id"]
            self.time_start = j.data.time.epoch
            self.save()

    def ui(self):
        url = "http://10.10.10.1:%s/attach/%s" % (self.client.port, self.corex_id)
        print("open browser to:%s" % url)

    def refresh(self):
        res = self._get_process_info()

        def update(res, state):
            dosave = False
            if not self.data.id:
                dosave = True

            assert self.corex_id == str(res["id"])

            if self.state != state:
                self.state = state
                dosave = True

            if self.time_refresh < j.data.time.epoch - 300:
                # means we write state every 5min no matter what
                dosave = True

            if self.pid != res["pid"]:
                self.pid = res["pid"]
                dosave = True

            self.time_refresh = j.data.time.epoch

            if dosave:
                self.save()

        if res:

            if res["state"] == "running":
                update(res, state="ok")

            elif res["state"] == "stopping":
                update(res, state="stopping")
            elif res["state"] == "stopped":
                update(res, state="stopped")

            else:
                j.shell()
        else:
            self.state = "stopped"

    def _get_process_info(self):
        res = self.client._process_list()
        if res == []:
            # means there is no process
            self._reset()
            return
        if self.data.id:
            for item in res:
                if int(item["id"]) == self.data.id:
                    return item
        for item in res:
            if int(item["pid"]) == self.pid:
                self.id = ""  # because other one no longer valid
                return item

    def _reset(self):
        self.time_start = 0
        self.time_stop = 0
        self.pid = 0
        self.state = "stopped"
        self.corex_id = ""


class CoreXProcessFactory(j.application.JSBaseConfigsClass):

    __jslocation__ = "j.data.corex_process"
    _CHILDCLASS = CoreXProcess

    def _init(self):
        pass
