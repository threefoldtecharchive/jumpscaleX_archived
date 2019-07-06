from Jumpscale import j
import requests

# import time
# import hmac
# from urllib.parse import urlencode
# from requests.auth import HTTPBasicAuth


class CoreXClient(j.application.JSBaseConfigClass):
    _SCHEMATEXT = """
    @url = jumpscale.corex.client.1
    name* = "" (S)
    addr = "localhost" (S)
    port = 7681 (I)
    login = "" (S)
    passwd_ = "" (S)
    
    """

    def _init(self):
        self._logger_enable()

    @property
    def _service_url(self):
        return "http://%s:%d/api/" % (self.addr, self.port)

    def _query(self, base_url, params=None, data=None, json=True, die=True):

        # request_conf = {"method": method, "url": self._service_url + base_url, "allow_redirects": True}

        # if params:
        #     # request_conf["url"] += "?" + urlencode(params)
        #     request_conf["url"] += "?" + params

        # if data:
        #     request_conf["data"] = data

        try:
            url = "%s/%s" % (self._service_url.rstrip("/"), base_url.lstrip("/"))
            if self.login != "":
                response = requests.get(url, auth=(self.login, self.passwd_), params=params)
            else:
                response = requests.get(url, params=params)
            # response = requests.request(**request_conf)
        except Exception as e:
            if str(e).find("Connection refused") != -1:
                raise RuntimeError("cannot connect to corex %s (%s:%s)" % (self.name, self.addr, self.port))
            raise e

        self._log_debug(url, data=params)

        if 300 > response.status_code >= 200:
            if json:
                try:
                    r = response.json()
                except Exception as e:
                    raise RuntimeError("json could not be decoded: %s (url:%s)" % (response.text, url))
                self._log_debug(r)
                if "status" in r and r["status"] == "error":
                    if r["reason"] == "process already stopped" and base_url.endswith("kill"):
                        return r
                    if not die:
                        return r
                    else:
                        raise RuntimeError("could not query:%s\n%s" % (url, r))
                return r

            else:
                return response.text
        else:
            raise ValueError("Http state {} - {}".format(response.status_code, response.content))

    def process_log_get(self, corex_id):
        r = self._corex_client._query("/process/logs", params={"id": corex_id}, json=False)

    def process_info_get(self, corex_id=None, pid=None):
        res = self.process_list()
        if corex_id:
            for item in res:
                if int(item["id"]) == corex_id:
                    return item
        if pid:
            for item in res:
                if int(item["pid"]) == pid:
                    self.id = ""  # because other one no longer valid
                    return item

    def ui_link_print(self, corex_id):
        url = "http://%s:%s/attach/%s" % (self.addr, self.port, corex_id)
        print("open browser to:%s" % url)

    def process_list(self):
        res = self._query("processes")
        return res["processes"]

    def process_kill(self, corex_id, signal=9, die=True):
        return self._query("/process/kill", params={"id": corex_id, "signal": signal}, die=die)

    def process_stop(self, corex_id):
        return self._query("/process/stop", params={"id": corex_id})

    def process_clean(self):
        """
        If a process stop/die/whatever, it stay on the list to get its state
        Clean remove all non running process from the list

        :return:
        """
        return self._query("/process/clean")
        # return r["state"] == "success"

    def process_start(self, cmd):
        """
        :param cmd: e.g. [‘mybib’, ‘-v’] or 'mybib -v'
        """
        assert cmd
        args = [arg for arg in cmd.split(" ")]
        params = {"arg[]": args}
        r = self._query("/process/start", params=params)
        return r
