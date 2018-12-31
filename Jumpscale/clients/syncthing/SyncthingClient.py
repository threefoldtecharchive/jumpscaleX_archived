#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests

import time
import pprint
from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass


class SyncthingClient(JSConfigClient):
    _SCHEMATEXT = """
    @url = jumpscale.syncthing.client
    name* = "" (S)
    addr = "localhost" (S)
    port = 0 (ipport)
    sshport = 22 (ipport)
    rootpasswd_ = "" (S)
    apikey = "" (S)
    """

    def _init(self):
        self._session = requests.session()
        addr = self.addr.lower()
        if addr == "127.0.0.1":
            addr = "localhost"
        self.addr = addr
        self.sshport = self.sshport
        self.rootpasswd = self.rootpasswd_
        self.port = self.port
        # TODO: need to be https
        self.syncthing_url = 'http://%s:%s/rest' % (self.addr, self.port)
        self.syncthing_apikey = self.apikey
        self._config = None

    def executeBashScript(self, cmds, die=True):
        self._logger.debug("execute cmd on %s" % self.addr)
        self._logger.debug(cmds)
        if self.addr == "localhost":
            return j.sal.process.execute(content=cmds, die=die)
        else:
            executor = j.tools.prefab.get(
                j.tools.executor.getSSHBased(addr=self.addr, port=self.sshport))
            return executor.prefab.core.execute_bash(content=cmds, die=die)

    def install(self, name=""):
        C = """
        set -ex
        tmux kill-session -t sync > /dev/null 2>&1;tmux new-session -d -s sync -n sync
        if [ "$(uname)" == "Darwin" ]; then
            # Do something under Mac OS X platform
            echo 'install brew'
            set +ex
            ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
            brew install curl
            brew install python
            brew install git
            brew install wget
            set -ex
            cd {DIR_TEMP}
            wget https://github.com/syncthing/syncthing/releases/download/v0.14.24/syncthing-macosx-amd64-v0.14.24.tar.gz -O syncthing.tar.gz
            tar -xf syncthing.tar.gz
            cd syncthing-macosx-amd64-v0.14.24
            cp syncthing /usr/local/bin/

        elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
            dist=''
            dist=`grep DISTRIB_ID /etc/*-release | awk -F '=' '{print $2}'`
            if [ "$dist" == "Ubuntu" ]; then
                echo "found ubuntu"
                apt-get install wget curl git ssh python2.7 python -y
            fi
            cd /tmp
            wget https://github.com/syncthing/syncthing/releases/download/v0.14.24/syncthing-linux-amd64-v0.14.24.tar.gz -O syncthing.tar.gz
            tar -xf syncthing.tar.gz
            cd syncthing-linux-amd64-v0.14.24
            cp syncthing /usr/local/bin/

        elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
            # Do something under Windows NT platform
            echo 'windows'
            echo "CODE NOT COMPLETE FOR WINDOWS IN install.sh"
            exit
        fi

        tmux send-keys -t sync "syncthing -gui-authentication=admin:$rootpasswd -gui-apikey=$apikey -gui-address=0.0.0.0:22001" C-m



        """
        C = C.replace("$rootpasswd", self.rootpasswd)
        C = C.replace("$apikey", self.syncthing_apikey)
        res = self.executeBashScript(C)

        self._logger.debug("check if we can find syncthing on right port: %s:%s" %
                           (self.addr, self.port))
        if j.sal.nettools.waitConnectionTest(self.addr, self.port, timeout=10) is False:
            raise j.exceptions.RuntimeError(
                "Could not find syncthing on %s:%s, tcp port test" % (self.addr, self.port))

            self._logger.debug(self.status_get())

    def restart(self):
        self._logger.debug("set config")
        pprint.pprint(self._config)
        self.config_set()
        self._logger.debug("restart")

        res = self.api_call("system/restart", get=False)
        self._logger.debug("wait for connection")
        time.sleep(0.5)
        j.sal.nettools.waitConnectionTest(self.addr, self.port, timeout=2)
        self._logger.debug("connection reestablished")

    def status_get(self):
        return self.api_call("system/status")

    def config_get(self, reload=False):
        if self._config is not None and reload is False:
            return self._config
        self._config = self.api_call("system/config")
        return self._config

    def config_set(self):
        self.api_call("system/config", get=False, data=self._config)

    def config_get_folders(self):
        config = self.config_get()
        return config["folders"]

    def config_get_devices(self):
        config = self.config_get()
        return config["devices"]

    def config_exists_folder(self, name):
        name = name.lower()
        for folder in self.config_get_folders():
            if folder["id"].lower() == name:
                return True
        return False

    def config_exists_device(self, name):
        name = name.lower()
        for device in self.config_get_devices():
            if device["name"].lower() == name:
                return True
        return False

    def id_get(self):
        return self.status_get()["myID"]

    def config_delete_folder(self, name):
        config = self.config_get()
        if self.config_exists_folder(name):
            # remove the folder
            x = len(self._config["folders"])
            res = []
            for folder in self._config["folders"]:
                if not folder["id"].lower() == name:
                    res.append(folder)
            self._config["folders"] = res
            if len(res) != x:
                self._logger.debug('deleted folder:%s' % name)
                # self.config_set()

    def config_delete_device(self, name):
        config = self.config_get()
        if self.config_exists_device(name):
            # remove the folder
            x = len(self._config["devices"])
            res = []
            for folder in self._config["devices"]:
                if not folder["name"].lower() == name:
                    res.append(folder)
            self._config["devices"] = res
            if len(res) != x:
                self._logger.debug('deleted devices:%s' % name)
                # self.config_set()

    def config_delete_all_folders(self):
        config = self.config_get()
        # remove the folder
        self._config["folders"] = []
        self._logger.debug('deleted all folder')
        # self.config_set()

    def config_delete_all_devices(self):
        config = self.config_get()
        # remove the folder
        self._config["devices"] = []
        self._logger.debug('deleted all devices')
        # self.config_set()

    def config_add_device(self, name, deviceid, replace=True, introducer=False, compression='always'):
        self._logger.debug("add device:%s" % name)
        name = name.lower()
        config = self.config_get()
        if self.config_exists_device(name):
            if replace:
                # remove the device
                res = []
                for device in self._config["devices"]:
                    if not device["name"].lower() == name:
                        res.append(device)
                self._config["devices"] = res
            else:
                raise j.exceptions.RuntimeError(
                    "Cannot add device %s, exists" % name)

        device = {'addresses': ['dynamic'],
                  'certName': '',
                  'compression': compression,
                  'deviceID': deviceid,
                  'introducer': introducer,
                  'name': name}

        config["devices"].append(device)

        self._logger.debug("device set:%s" % name)

        # self.config_set()
        return device

    def config_add_folder(self, name, path, replace=True, ignorePerms=False,
                          readOnly=False, rescanIntervalS=10, devices=[]):
        name = name.lower()
        config = self.config_get()
        if self.config_exists_folder(name):
            if replace:
                # remove the folder
                res = []
                for folder in self._config["folders"]:
                    if not folder["id"].lower() == name:
                        res.append(folder)
                self._config["folders"] = res
            else:
                raise j.exceptions.RuntimeError(
                    "Cannot add folder %s, exists" % name)

        if self.id_get() not in devices:
            devices.append(self.id_get())

        if devices != []:
            devices = [{'deviceID': item} for item in devices]

        folder = {'autoNormalize': False,
                  'copiers': 0,
                  'devices': devices,
                  'hashers': 0,
                  'id': name,
                  'ignoreDelete': False,
                  'ignorePerms': ignorePerms,
                  'invalid': '',
                  'minDiskFreePct': 5,
                  'order': 'random',
                  'path': path,
                  'pullers': 0,
                  'readOnly': readOnly,
                  'rescanIntervalS': rescanIntervalS,
                  'versioning': {'params': {}, 'type': ''}}
        config["folders"].append(folder)

        self._logger.debug("folder set:%s" % name)

        self.executeBashScript("mkdir -p %s" % path)
        self.restart()
        # self.config_set()
        return folder

    def api_call(self, endpoint, request_body=False, get=True, data=None):
        """
        @param data is dict which can be serialized using json (do not serialize yet)
        """

        endpoint = endpoint.strip("/")
        endpoint = "/%s" % endpoint

        url = '%s%s' % (self.syncthing_url, endpoint)

        headers = {'Content-Type': 'application/json',
                   'User-Agent': 'Syncthing Python client', 'X-API-Key': self.syncthing_apikey}

        if request_body:
            keys = list(request_body.keys())

            key = keys[0]
            keys.remove(key)

            url += '?%s=%s' % (key, request_body[key])

            for key in keys:
                url += '&%s=%s' % (key, request_body[key])

        timeout = 10
        start = time.time()
        ok = False
        self._logger.debug(url)
        while time.time() < (start + timeout) and ok is False:
            try:
                if get:
                    r = requests.get(url, headers=headers, timeout=2)
                else:
                    r = requests.post(url, headers=headers,
                                      json=data, timeout=2)
                ok = True
            except Exception as e:
                self._logger.warn(
                    "Warning, Error in API call, will retry:\n%s" % e)
                self._logger.warn("retry API CALL %s" % url)
                time.sleep(0.2)

        if ok is False or r.ok is False:
            self._logger.error("%s" % (url))
            self._logger.error(endpoint)
            self._logger.error(request_body)
            raise j.exceptions.RuntimeError("Error in rest call: %s" % r)

        if get and endpoint != '/system/version':
            return r.json()

        self._logger.debug("OK")

        return r.content
