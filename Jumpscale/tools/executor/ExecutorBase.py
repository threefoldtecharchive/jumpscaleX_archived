from Jumpscale import j

import base64
from .ExecutorInstallers import ExecutorInstallers

JSBASE = j.application.JSBaseClass


class ExecutorBase(j.application.JSBaseClass):
    def __init__(self, debug=False, checkok=True):
        self.debug = debug
        self.checkok = checkok
        self.type = None

        self._id = None
        self._env = {}
        self.readonly = False
        self.CURDIR = ""

        # self._state = None

        JSBASE.__init__(self)

        self.installer = ExecutorInstallers(executor=self)

        self._env_on_system = None

        self._init3()

    def reset(self):
        self.state_reset()
        self.env_on_system_msgpack = ""
        self.config_msgpack = ""
        self.save()
        self._init3()

    def _init3(self):

        self._env_on_system = None

        if self.config_msgpack != b"":
            self.config = j.data.serializers.msgpack.loads(self.config_msgpack)
        else:
            self.config = {}

        if "state" not in self.config:
            self.config["state"] = {}

    def save(self):
        """
        only relevant for ssh
        :return:
        """
        pass

    @property
    def data(self):
        return self.sshclient.data

    def delete(self, path):
        path = self._replace(path)
        cmd = "rm -rf %s" % path
        self.execute(cmd)

    def exists(self, path):
        path = self._replace(path)
        rc, _, _ = self.execute("test -e %s" % path, die=False, showout=False)
        if rc > 0:
            return False
        else:
            return True

    def _replace(self, content, args=None):
        """
        args will be substitued to .format(...) string function https://docs.python.org/3/library/string.html#formatspec
        MyEnv.config will also be given to the format function

        content example:

        "{name!s:>10} {val} {n:<10.2f}"  #floating point rounded to 2 decimals

        performance is +100k per sec
        """
        if self.type == "ssh":
            content = self.sshclient._replace(content)
        return j.core.tools.text_replace(content=content, args=args, executor=self)

    def dir_ensure(self, path):
        cmd = "mkdir -p %s" % path
        self.execute(cmd)

    def path_isdir(self, path):
        """
        checks if the path is a directory
        :return:
        """
        rc, out, err = self.execute('if [ -d "%s" ] ;then echo DIR ;fi' % path)
        return out.strip() == "DIR"

    def path_isfile(self, path):
        """
        checks if the path is a directory
        :return:
        """
        rc, out, err = self.execute('if [ -f "%s" ] ;then echo FILE ;fi' % path)
        return out.strip() == "FILE"

    @property
    def platformtype(self):
        return j.core.platformtype.get(self)

    def file_read(self, path):
        self._log_debug("file read:%s" % path)
        rc, out, err = self.execute("cat %s" % path, showout=False)
        return out

    def file_write(self, path, content, mode=None, owner=None, group=None, append=False, sudo=False, showout=True):
        """
        @param append if append then will add to file

        if file bigger than 100k it will not set the attributes!

        """
        path = self._replace(path)
        if showout:
            self._log_debug("file write:%s" % path)

        if len(content) > 100000:
            # when contents are too big, bash will crash
            temp = j.sal.fs.getTempFileName()
            j.sal.fs.writeFile(filename=temp, contents=content, append=False)
            self.upload(temp, path, showout=showout)
            j.sal.fs.remove(temp)
        else:
            content2 = content.encode("utf-8")
            # sig = hashlib.md5(content2).hexdigest()
            parent = j.sal.fs.getParent(path)
            cmd = "set -e;mkdir -p %s\n" % parent

            content_base64 = base64.b64encode(content2).decode()
            # cmd += 'echo "%s" | openssl base64 -D '%content_base64   #DONT
            # KNOW WHERE THIS COMES FROM?
            cmd += 'echo "%s" | openssl base64 -A -d ' % content_base64

            if append:
                cmd += ">> %s\n" % path
            else:
                cmd += "> %s\n" % path

            if mode:
                cmd += "chmod %s %s\n" % (mode, path)
            if owner:
                cmd += "chown %s %s\n" % (owner, path)
            if group:
                cmd += "chgrp %s %s\n" % (group, path)

            res = self.execute(cmd, showout=False, script=False)

        return None

    @property
    def uid(self):
        if self._id is None:
            raise RuntimeError("self._id cannot be None")
        return self._id

    def _commands_transform(self, cmds, die=True, checkok=False, env={}, sudo=False, shell=False):
        # print ("TRANSF:%s"%cmds)

        if sudo or shell:
            checkok = False

        multicommand = "\n" in cmds or ";" in cmds

        if shell:
            if "\n" in cmds:
                raise RuntimeError("cannot do shell for multiline scripts")
            else:
                cmds = "bash -c '%s'" % cmds

        pre = ""

        checkok = checkok or self.checkok

        if die:
            # first make sure not already one
            if "set -e" not in cmds:
                # now only do if multicommands
                if multicommand:
                    if self.debug:
                        pre += "set -ex\n"
                    else:
                        pre += "set -e\n"

        if self.CURDIR != "":
            pre += "cd %s\n" % (self.CURDIR)

        if env != {}:
            for key, val in env.items():
                pre += "export %s=%s\n" % (key, val)

        cmds = "%s\n%s" % (pre, cmds)

        if checkok and multicommand:
            if not cmds.endswith("\n"):
                cmds += "\n"
            cmds += "echo '**OK**'"

        if "\n" in cmds:
            cmds = cmds.replace("\n", ";")
            cmds.strip() + "\n"

        cmds = cmds.replace(";;", ";").strip(";")

        if sudo:
            cmds = self.sudo_cmd(cmds)

        self._log_debug(cmds)

        return cmds

    def exists(self, path):
        raise NotImplemented()

    def find(self, path):
        rc, out, err = self.execute("find %s" % path, die=False)
        if rc > 0:
            if err.lower().find("no such file") != -1:
                return []
            raise RuntimeError("could not find:%s \n%s" % (path, err))
        res = []
        for line in out.split("\n"):
            if line.strip() == path:
                continue
            if line.strip() == "":
                continue
            res.append(line)
        res.sort()
        return res

    # interface to implement by child classes
    def execute(self, *args, **kwargs):
        raise NotImplementedError()

    # def executeRaw(self, cmd, die=True, showout=False):
    #     raise NotImplementedError()

    @property
    def isDebug(self):
        return (
            self.state.configGetFromDict("system", "debug") == "1"
            or self.state.configGetFromDict("system", "debug") == 1
            or self.state.configGetFromDict("system", "debug")
            or self.state.configGetFromDict("system", "debug") == "true"
        )

    @property
    def isContainer(self):
        """
        means we don't work with ssh-agent ...
        """
        return self.env_on_system["iscontainer"]

    @property
    def isSandbox(self):
        """
        has this env a sandbox?
        """
        if self._isSandbox is None:
            if self.exists("/sandbox"):
                self._isSandbox = True
            else:
                self._isSandbox = False
        return self._isSandbox

    def debug_enable(self):
        self.state.configSetInDictBool("system", "debug", True)
        self.state.configSave()
        self._cache.reset()

    # def _initEnv(self):
    #     """
    #     init the environment of an executor
    #     """
    #
    #     self._env = self.env_on_system["env"]
    #
    #     self.env_on_system
    #
    #     print("INITENV")  # TMP
    #     self.reset()
    #     j.shell()
    #     w
    #
    #     self.config["system"]["container"] = self.env_on_system["iscontainer"]
    #
    #     if self.isBuildEnv:
    #         # ONLY RELEVANT FOR BUILDING PYTHON, needs to check what needs to be done (kristof) #TODO:
    #         j.shell()
    #
    #     else:
    #         out = ""
    #         for key, val in self.dir_paths.items():
    #             out += "mkdir -p %s\n" % val
    #         self.execute(out, sudo=True, showout=False)
    #
    #     self._cache.reset()
    #
    #     self.config["system"]["executor"] = True
    #     self.config["DIRS"]["HOMEDIR"] = self.env_on_system["HOME"]
    #     self.state.configSave()
    #
    #     if "cfg_state" in self.env_on_system:
    #         self.state._state = self.env_on_system["cfg_state"]
    #
    #     self._log_debug("initenv done on executor base")

    @property
    def cache(self):
        if self._cache is None:
            self._cache = j.core.cache.get("executor" + self.uid, reset=True, expiration=600)  # 10 min
        return self._cache

    @property
    def platformtype(self):
        return j.core.platformtype.get(self)

    # def sudo_cmd(self, command):
    #
    #     if "\n" in command:
    #         raise RuntimeError("cannot do sudo when multiline script:%s" % command)
    #
    #     if hasattr(self, "sshclient"):
    #         login = self.sshclient.config.data["login"]
    #         passwd = self.sshclient.config.data["passwd_"]
    #     else:
    #         login = getattr(self, "login", "")
    #         passwd = getattr(self, "passwd", "")
    #
    #     if "darwin" in self.platformtype.osname:
    #         return command
    #     if login == "root":
    #         return command
    #
    #     passwd = passwd or "''"
    #
    #     cmd = "echo %s | sudo -H -SE -p '' bash -c \"%s\"" % (passwd, command.replace('"', '\\"'))
    #     return cmd

    @property
    def env_on_system(self):
        if not self._env_on_system:
            if self.env_on_system_msgpack == b"":
                self.systemenv_load()
            self._env_on_system = j.data.serializers.msgpack.loads(self.env_on_system_msgpack)
        return self._env_on_system

    @property
    def env(self):
        return self.env_on_system["ENV"]

    @property
    def state(self):
        if "state" not in self.config:
            self.config["state"] = {}
        return self.config["state"]

    def state_exists(self, key):
        key = j.core.text.strip_to_ascii_dense(key)
        return key in self.state

    def state_set(self, key, val=None, save=True):
        key = j.core.text.strip_to_ascii_dense(key)
        if key not in self.state or self.state[key] != val:
            self.state[key] = val
            self.save()

    def state_get(self, key, default_val=None):
        key = j.core.text.strip_to_ascii_dense(key)
        if key not in self.state:
            if default_val:
                self.state[key] = default_val
                return default_val
            else:
                return None
        else:
            return self.state[key]

    def state_delete(self, key):
        key = j.core.text.strip_to_ascii_dense(key)
        if key in self.state:
            self.state.pop(key)

    def state_reset(self):
        self.config["state"] = {}

    def systemenv_load(self):
        """
        get relevant information from remote system e.g. hostname, env variables, ...
        :return:
        """
        C = """
        set +ex
        ls "/sandbox"  > /dev/null 2>&1 && echo 'ISSANDBOX = 1' || echo 'ISSANDBOX = 0'

        ls "/sandbox/bin/python3"  > /dev/null 2>&1 && echo 'ISSANDBOX_BIN = 1' || echo 'ISSANDBOX_BIN = 0'                        

        echo UNAME = \""$(uname -mnprs)"\"

        echo "HOME = $HOME"

        echo HOSTNAME = "$(hostname)"

        echo OS_TYPE = "ubuntu"

        # lsmod > /dev/null 2>&1|grep vboxdrv |grep -v grep  > /dev/null 2>&1 && echo 'VBOXDRV=1' || echo 'VBOXDRV=0'

        # #OS
        # apt-get -v > /dev/null 2>&1 && echo 'OS_TYPE="ubuntu"'
        # test -f /etc/arch-release > /dev/null 2>&1 && echo 'OS_TYPE="arch"'
        # test -f /etc/redhat-release > /dev/null 2>&1 && echo 'OS_TYPE="redhat"'
        # apk -v > /dev/null 2>&1 && echo 'OS_TYPE="alpine"'
        # brew -v > /dev/null 2>&1 && echo 'OS_TYPE="darwin"'
        # opkg -v > /dev/null 2>&1 && echo 'OS_TYPE="LEDE"'
        # cat /etc/os-release | grep "VERSION_ID"
        # 

        echo "CFG_JUMPSCALE = --TEXT--"
        cat /sandbox/cfg/jumpscale_config.msgpack 2>/dev/null || echo ""
        echo --TEXT--

        echo "BASHPROFILE = --TEXT--"
        cat $HOME/.profile_js 2>/dev/null || echo ""
        echo --TEXT--

        echo "ENV = --TEXT--"
        export
        echo --TEXT--
        """
        rc, out, err = self.execute(C, showout=False, interactive=False, replace=False)
        res = {}
        state = ""
        for line in out.split("\n"):
            if line.find("--TEXT--") != -1 and line.find("=") != -1:
                varname = line.split("=")[0].strip().lower()
                state = "TEXT"
                txt = ""
                continue

            if state == "TEXT":
                if line.strip() == "--TEXT--":
                    res[varname.upper()] = txt
                    state = ""
                    continue
                else:
                    txt += line + "\n"
                    continue

            if "=" in line:
                varname, val = line.split("=", 1)
                varname = varname.strip().lower()
                val = str(val).strip().strip('"')
                if val.lower() in ["1", "true"]:
                    val = True
                elif val.lower() in ["0", "false"]:
                    val = False
                else:
                    try:
                        val = int(val)
                    except BaseException:
                        pass
                res[varname.upper()] = val

        if res["CFG_JUMPSCALE"].strip() != "":
            rconfig = j.core.tools.config_load(content=res["CFG_JUMPSCALE"])
            res["CFG_JUMPSCALE"] = rconfig
        else:
            res["CFG_JUMPSCALE"] = {}

        envdict = {}
        for line in res["ENV"].split("\n"):
            line = line.replace("declare -x", "")
            line = line.strip()
            if line.strip() == "":
                continue
            if "=" in line:
                pname, pval = line.split("=", 1)
                pval = pval.strip("'").strip('"')
                envdict[pname.strip().upper()] = pval.strip()

        res["ENV"] = envdict

        def get_cfg(name, default):
            name = name.upper()
            if "CFG_JUMPSCALE" in res and name in res["CFG_JUMPSCALE"]:
                self.config[name] = res["CFG_JUMPSCALE"]
                return
            if name not in self.config:
                self.config[name] = default

        get_cfg("DIR_HOME", res["ENV"]["HOME"])
        get_cfg("DIR_BASE", "/sandbox")
        get_cfg("DIR_CFG", "/sandbox/cfg")
        get_cfg("DIR_TEMP", "/tmp")
        get_cfg("DIR_VAR", "/sandbox/var")
        get_cfg("DIR_CODE", "/sandbox/code")
        get_cfg("DIR_BIN", "/usr/local/bin")

        self.env_on_system_msgpack = j.data.serializers.msgpack.dumps(res)
        self.save()

    #
    # def system_install(self,force=False,sandbox=False):
    #
    #     if force or notself.state_exists("myenv_init"):
    #
    #         if j.core.tools.platform()== "linux":
    #             script="""
    #             echo >> /etc/apt/sources.list
    #             echo "# Jumpscale Setup" >> /etc/apt/sources.list
    #             echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
    #             apt-get update
    #
    #             apt-get install -y curl rsync unzip
    #             locale-gen --purge en_US.UTF-8
    #
    #             mkdir -p /tmp/jumpscale/scripts
    #             mkdir -p /sandbox/var/log
    #
    #             """
    #         else:
    #             if not j.core.tools.cmd_installed("curl") or j.core.tools.cmd_installed("unzip") or j.core.tools.cmd_installed("rsync"):
    #                 script="""
    #                 brew install curl unzip rsync
    #                 """
    #             else:
    #                 script = ""
    #                 j.core.tools.error_raise("Cannot continue, curl, rsync, unzip needs to be installed")
    #
    #         j.core.tools.execute(script,interactive=True)
    #
    #
    #         self.config_load()
    #
    #         if not "HOME" in self.config and "HOME" in os.environ:
    #            self.config["DIR_HOME"] = copy.copy(os.environ["HOME"])
    #            self.config_save()
    #
    #         if not os.path.exists(MyEnv.config["DIR_BASE"]):
    #             script = """
    #             cd /
    #             sudo mkdir -p /sandbox/cfg
    #             sudo chown -R {USERNAME}:{GROUPNAME} /sandbox
    #             """
    #             args={}
    #             args["USERNAME"] = getpass.getuser()
    #             st = os.stat(MyEnv.config["DIR_HOME"])
    #             gid = st.st_gid
    #             args["GROUPNAME"] = grp.getgrgid(gid)[0]
    #             j.core.tools.execute(script,interactive=True,args=args)
    #
    #
    #         installed = j.core.tools.cmd_installed("git") and j.core.tools.cmd_installed("ssh-agent")
    #        self.config["SSH_AGENT"]=installed
    #        self.config_save()
    #
    #             # and
    #         if not os.path.exists(ExecutorMyEnv.config["DIR_TEMP"]):
    #             os.makedirs(ExecutorMyEnv.config["DIR_TEMP"], exist_ok=True)
    #
    #        self.state_set("myenv_init")
    #
    #     if os.path.exists(os.path.join(ExecutorMyEnv.config["DIR_BASE"], "bin", "python3.6")):
    #        self.sandbox_python_active=True
    #     else:
    #        self.sandbox_python_active=False
    #
    #
    #     #will get the sandbox installed
    #     if force or notself.state_exists("myenv_install"):
    #
    #         ifself.config["INSYSTEM"]:
    #
    #             #DONT USE THE SANDBOX
    #
    #             UbuntuInstall.do_all()
    #
    #             j.core.tools.code_github_get(repo="sandbox_base", branch=["master"])
    #
    #             script="""
    #             set -e
    #             cd {DIR_BASE}
    #             rsync -ra code/github/threefoldtech/sandbox_base/base/ .
    #
    #             #remove parts we don't use in in system deployment
    #             rm -rf {DIR_BASE}/openresty
    #             rm -rf {DIR_BASE}/lib/python
    #             rm -rf {DIR_BASE}/lib/pythonbin
    #             rm -rf {DIR_BASE}/var
    #             rm -rf {DIR_BASE}/root
    #
    #             mkdir -p root
    #             mkdir -p var
    #
    #             """
    #             j.core.tools.execute(script,interactive=True)
    #
    #
    #
    #         else:
    #
    #             j.core.tools.code_github_get(repo="sandbox_base", branch=["master"])
    #
    #             script="""
    #             cd {DIR_BASE}
    #             rsync -ra code/github/threefoldtech/sandbox_base/base/ .
    #             mkdir -p root
    #             """
    #             j.core.tools.execute(script,interactive=True)
    #
    #             if j.core.tools.platform() == "darwin":
    #                 reponame = "sandbox_osx"
    #             elif j.core.tools.platform() == "linux":
    #                 reponame = "sandbox_ubuntu"
    #             else:
    #                 raise RuntimeError("cannot install, j.core.tools.platform() now found")
    #
    #             j.core.tools.code_github_get(repo=reponame, branch=["master"])
    #
    #             script="""
    #             set -ex
    #             cd {DIR_BASE}
    #             rsync -ra code/github/threefoldtech/{REPONAME}/base/ .
    #             mkdir -p root
    #             mkdir -p var
    #             """
    #             args={}
    #             args["REPONAME"]=reponame
    #
    #             j.core.tools.execute(script,interactive=True,args=args)
    #
    #             script="""
    #             set -e
    #             cd {DIR_BASE}
    #             source env.sh
    #             python3 -c 'print("- PYTHON OK, SANDBOX USABLE")'
    #             """
    #             j.core.tools.execute(script,interactive=True)
    #
    #         j.core.tools.log("INSTALL FOR BASE OK")
    #
    #        self.state_set("myenv_install")

    def test(self):

        """
        kosmos 'j.tools.executor.local.test()'
        :return:
        """
        ex = self

        ex.reset()

        assert ex.state == {}
        assert ex.env_on_system_msgpack == ""
        assert ex.config_msgpack == ""

        rc, out, err = ex.execute("ls /")
        assert rc == 0
        assert err == ""
        assert out.endswith("\n")

        ex.state_set("bla")
        assert ex.state == {"bla": None}
        assert ex.state_exists("bla")
        assert ex.state_exists("blabla") == False
        assert ex.state_get("bla") == None
        ex.state_reset()
        assert ex.state_exists("bla") == False
        assert ex.state == {}
        ex.state_set("bla", 1)
        assert ex.state == {"bla": 1}

        e = ex.env_on_system

        assert e["HOME"] == j.core.myenv.config["DIR_HOME"]

        ex.file_write("/tmp/1re", "a")
        assert ex.file_read("/tmp/1re").strip() == "a"

        assert ex.path_isdir("/tmp")
        assert ex.path_isfile("/tmp") == False
        assert ex.path_isfile("/tmp/1re")

        path = ex.download("/tmp/1re", "/tmp/something.txt")
        path = ex.upload("/tmp/something.txt", "/tmp/2re")

        assert ex.file_read("/tmp/2re").strip() == "a"

        assert j.sal.fs.readFile("/tmp/something.txt").strip() == "a"
        j.sal.fs.remove("/tmp/something.txt")

        j.sal.fs.createDir("/tmp/8888")
        j.sal.fs.createDir("/tmp/8888/5")
        j.sal.fs.writeFile("/tmp/8888/1.txt", "a")
        j.sal.fs.writeFile("/tmp/8888/2.txt", "a")
        j.sal.fs.writeFile("/tmp/8888/5/3.txt", "a")

        path = ex.upload("/tmp/8888", "/tmp/8889")

        ex.delete("/tmp/2re")
        ex.delete("/tmp/1re")

        r = ex.find("/tmp/8889")
        assert r == ["/tmp/8889/1.txt", "/tmp/8889/2.txt", "/tmp/8889/5", "/tmp/8889/5/3.txt"]

        j.sal.fs.remove("/tmp/8889")

        ex.download("/tmp/8888", "/tmp/8889")

        r2 = j.sal.fs.listFilesAndDirsInDir("/tmp/8889")
        r2.sort()
        assert r2 == ["/tmp/8889/1.txt", "/tmp/8889/2.txt", "/tmp/8889/5", "/tmp/8889/5/3.txt"]

        ex.delete("/tmp/8888")
        r2 = ex.find("/tmp/8888")
        assert r2 == []

        j.sal.fs.remove("/tmp/8888")
        j.sal.fs.remove("/tmp/8889")

        ex.reset()
        assert ex.state == {}
        assert ex.env_on_system_msgpack == ""
        assert ex.config_msgpack == ""

        # test that it does not do repeating thing & cache works
        for i in range(1000):
            ptype = self.platformtype

        for i in range(1000):
            env = self.env

        self._log_info("TEST for executor done")
