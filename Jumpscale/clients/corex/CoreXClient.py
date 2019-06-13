from Jumpscale import j
import requests
import time
import hmac
from urllib.parse import urlencode


class CoreXClient(j.application.JSBaseConfigClass):
    _SCHEMATEXT = """
    @url = jumpscale.corex.client
    name* = "" (S)
    addr = "" (S)
    port = 7681 (I)
    login = "" (S)
    passwd_ = "" (S)
    cmd = "" (S)
    
    """

    def _init(self):
        self._service_url = "http://%s:%d/api/" % (self.addr, self.port)

    def _query(self, base_url, params=None, data=None, json=True):

        # request_conf = {"method": method, "url": self._service_url + base_url, "allow_redirects": True}

        # if params:
        #     # request_conf["url"] += "?" + urlencode(params)
        #     request_conf["url"] += "?" + params

        # if data:
        #     request_conf["data"] = data

        if self.login != "":
            request_conf["headers"] = self._get_headers(data or {})

        try:
            response = requests.get("%s/%s" % (self._service_url, base_url), params=params)
            # response = requests.request(**request_conf)
        except Exception as e:
            if str(e).find("Connection refused") != -1:
                raise RuntimeError("cannot connect to corex %s (%s:%s)" % (self.name, self.addr, self.port))
            raise e

        if 300 > response.status_code >= 200:
            if json:
                try:
                    return response.json()
                except Exception as e:
                    j.shell()
            else:
                return response.text
        else:
            raise ValueError("Http state {} - {}".format(response.status_code, response.content))

    def _get_headers(self, data):
        msg = self.key_ + urlencode(sorted(data.items(), key=lambda val: val[0]))

        sign = hmac.new(self.secret_.encode(), msg.encode(), digestmod="sha256").hexdigest()

        return {"X-KEY": self.key_, "X-SIGN": sign, "X-NONCE": str(int(time() * 1000))}

    def _process_list(self):
        res = self._query("processes")
        return res["processes"]

    def process_clean(self):
        """
        If a process stop/die/whatever, it stay on the list to get its state
        Clean remove all non running process from the list

        :return:
        """
        # TODO:
        r = requests.get(self._endpoint("/process/clean")).json()
        return r["state"] == "success"

    def process_start(self, name, cmd, kill=False, ports=[]):
        """
        :param cmd: e.g. [‘mybib’, ‘-v’] or 'mybib -v'
        :param kill, if kill it means will stop the process when it exists
        :return: id of the process
        """
        p = j.data.corex_process.get(name=name, die=False)
        p.client = self
        p.corex_name = self.name
        if p.data.id:
            # means data already existed
            p.start(kill=kill)
        else:
            p.cmd = cmd
            p.ports = ports
            p.start()

        return p

    def process_get(self, name=None, id=None, pid=None, corex_id=None, die=False, refresh=True):
        """
        try and find the process in local DB, if not found then will create one based on what it can find on server
        :param name: is required
        :param id: if of process in corex
        :param pid: process id
        :param die, if False then will create an object if not found
        :param refresh, if refresh then will get the state from the corex server
        :return: CoreXProcess JSX object
        """
        if name:
            assert id == None
            assert pid == None
            p = j.data.corex_process.get(name=name, die=False)
            if not p:
                if die:
                    raise RuntimeError("cannot find process with name:%s" % name)
                else:
                    p = j.data.corex_process.new(name=name)
        elif id:
            p = j.data.corex_process.get(id=id, die=False)
            if not p:
                if die:
                    raise RuntimeError("cannot find process with id:%s" % id)
                else:
                    p = j.data.corex_process.new(name=name)
        elif pid:
            res = j.data.corex_process.find(pid=pid, corex_name=self.name)
            if len(res) > 1:
                raise RuntimeError("found more than 1 process:%s with pid:%s" % (res, pid))
            elif len(res) == 0:
                if die:
                    raise RuntimeError("cannot find process with pid:%s" % pid)
                else:
                    p = j.data.corex_process.new(name=name)
            else:
                p = res[0]

        elif corex_id:
            res = j.data.corex_process.find(corex_id=corex_id, corex_name=self.name)
            if len(res) > 1:
                raise RuntimeError("found more than 1 process:%s" % res)
            elif len(res) == 0:
                if die:
                    raise RuntimeError("cannot find process with corex_id:%s" % corex_id)
                else:
                    p = j.data.corex_process.new(name=name)
            else:
                p = res[0]
        else:
            raise RuntimeError(
                "should specify name or id or pid or corex_id now was (%s,%s,%s,%s)" % (name, id, pid, corex_id)
            )

        p.client = self
        p.corex_name = self.name
        if refresh:
            p.refresh()
        return p

    def ssh_start(self, port=22, pubkeys=[]):
        """
        :param pubkeys:
        :return:
        """
        if pubkeys is []:
            pubkeys = [j.clients.sshagent.key_pub_get()]
        pass
