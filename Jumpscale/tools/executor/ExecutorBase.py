from Jumpscale import j
import pytoml

import base64
import os

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

        self._config = None
        self._state = None

        self._config_hash = ""
        self._config_path = "/sandbox/cfg/jumpscale_config.toml"

        JSBASE.__init__(self)

        self.reset()

    def text_strip(self, content, ignorecomments=True, args={}, args_replace=True):
        """
        remove all spaces at beginning & end of line when relevant (this to allow easy definition of scripts)
        args will be substitued to .format(...) string function https://docs.python.org/3/library/string.html#formatspec
        MyEnv.config will also be given to the format function


        for examples see text_replace method


        """

        return j.core.tools.text_strip(content=content, ignorecomments=ignorecomments, args=args,
                                       args_replace=args_replace, executor=self)

    def replace(self, content, args=None):
        """
        args will be substitued to .format(...) string function https://docs.python.org/3/library/string.html#formatspec
        MyEnv.config will also be given to the format function

        content example:

        "{name!s:>10} {val} {n:<10.2f}"  #floating point rounded to 2 decimals

        performance is +100k per sec
        """

        return j.core.tools.text_replace(content=content, args=args, executor=self)

    @property
    def config(self):
        if self._config is None:
            r = j.core.db.get("executor:%s:config" % self.id)
            if r is None:
                self.config_load()
            else:
                self._config = j.data.serializers.json.loads(r)
                self._config_hash = j.data.hash.md5_string(r)
        return self._config

    def config_load(self):
        """
        only 1 level deep toml format only for int,string,bool
        no multiline
        """
        self._config = j.core.tools.config_load(self._config_path, executor=self)
        if self._config == {}:
            self._config = j.core.myenv.config_default_get()
            # TODO Fix the executor state
            self._config["DIR_HOME"] = "/root"  # self.state_on_system["HOME"]
        self.config_save(False)

    def config_save(self, onsystem=True):
        data = j.data.serializers.json.dumps(self._config)
        if onsystem and self._config_hash != j.data.hash.md5_string(data):
            j.core.tools.config_save(self._config_path, self.config, executor=self)
        j.core.db.set("executor:%s:config" % self.id, data, ex=3600)
        self._config_hash = j.data.hash.md5_string(data)

    def state_exists(self, key):
        key = j.core.text.strip_to_ascii_dense(key)
        return j.core.db.hget("executor:%s:state" % self.id, key) != None

    def state_set(self, key, val=None):
        key = j.core.text.strip_to_ascii_dense(key)
        val2 = j.data.serializers.json.dumps(val)
        j.core.db.hset("executor:%s:state" % self.id, key, val2)

    def state_get(self, key, default_val=None):
        key = j.core.text.strip_to_ascii_dense(key)
        r = j.core.db.hget("executor:%s:state" % self.id, key)
        if r is None:
            self.state_set(key, val=default_val)
        else:
            return j.data.serializers.json.loads(r)

    def state_delete(self, key):
        key = j.core.text.strip_to_ascii_dense(key)
        j.core.db.hdel("executor:%s:state" % self.id, key)

    def state_deleteall(self):
        j.core.db.delete("executor:%s:state" % self.id)

    def reset(self):
        self._state_on_system = None
        self._prefab = None
        self._state = None
        self._state_on_system = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = j.logger.get("executor")
        return self._logger

    @property
    def id(self):
        if self._id is None:
            raise RuntimeError("self._id cannot be None")
        return self._id

    @property
    def env(self):
        if self._env == {}:
            self._env = self.state_on_system["env"]
        return self._env

    def _docheckok(self, cmd, out):
        out = out.rstrip("\n")
        lastline = out.split("\n")[-1]
        if lastline.find("**OK**") == -1:
            raise RuntimeError("Error in:\n%s\n***\n%s" % (cmd, out))
        out = "\n".join(out.split("\n")[:-1]).rstrip() + "\n"
        return out

    def commands_transform(
            self,
            cmds,
            die=True,
            checkok=False,
            env={},
            sudo=False,
            shell=False):
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
            if not cmds.endswith('\n'):
                cmds += '\n'
            cmds += "echo '**OK**'"

        if "\n" in cmds:
            cmds = cmds.replace("\n", ";")
            cmds.strip() + "\n"

        cmds = cmds.replace(";;", ";").strip(";")

        if sudo:
            cmds = self.sudo_cmd(cmds)

        self._logger.debug(cmds)

        return cmds

    def exists(self, path):
        raise NotImplemented()

    # interface to implement by child classes
    def execute(
            self,
            cmds,
            die=True,
            checkok=None,
            showout=True,
            timeout=0,
            env={},
            sudo=False):
        raise NotImplementedError()

    def executeRaw(self, cmd, die=True, showout=False):
        raise NotImplementedError()

    @property
    def isDebug(self):
        return self.state.configGetFromDict(
            "system", "debug") == "1" or self.state.configGetFromDict(
            "system", "debug") == 1 or self.state.configGetFromDict(
            "system", "debug") or self.state.configGetFromDict(
            "system", "debug") == "true"

    @property
    def isContainer(self):
        """
        means we don't work with ssh-agent ...
        """
        return self.state_on_system["iscontainer"]

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

    @property
    def state_on_system(self):
        """
        is dict of all relevant param's on system
        """
        if self._state_on_system == None:

            self._logger.debug("stateonsystem for non local:%s" % self)
            C = """
            set +ex
            ls "/sandbox"  > /dev/null 2>&1 && echo 'ISSANDBOX = 1' || echo 'ISSANDBOX = 0'

            ls "/sandbox/bin/python3"  > /dev/null 2>&1 && echo 'ISSANDBOX_BIN = 1' || echo 'ISSANDBOX_BIN = 0'                        

            if [ ! -f /tmp/uid.txt ]; then
                echo $RANDOM > /tmp/uid.txt
            fi
            echo UID = `cat /tmp/uid.txt`                    

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
            cat {_config_path} 2>/dev/null || echo ""
            echo --TEXT--

            echo "BASHPROFILE = --TEXT--"
            cat $HOME/.profile_js 2>/dev/null || echo ""
            echo --TEXT--

            echo "ENV = --TEXT--"
            export
            echo --TEXT--
            """
            C = j.core.text.strip(C,args=self.__dict__)

            rc, out, err = self.execute(C, showout=False, sudo=False, replace=False)
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
                        res[varname] = txt
                        state = ""
                        continue
                    else:
                        txt += line + "\n"
                        continue

                if "=" in line:
                    varname, val = line.split("=", 1)
                    varname = varname.strip().lower()
                    val = str(val).strip().strip("\"")
                    if val.lower() in ["1", "true"]:
                        val = True
                    elif val.lower() in ["0", "false"]:
                        val = False
                    else:
                        try:
                            val = int(val)
                        except BaseException:
                            pass
                    res[varname] = val

            if res["cfg_jumpscale"].strip() != "":
                rconfig = j.core.tools.config_load(content=res["cfg_jumpscale"])
                res["cfg_jumpscale"] = rconfig
            else:
                res["cfg_jumpscale"] = {}

            envdict = {}
            for line in res["env"].split("\n"):
                line = line.replace("declare -x", "")
                line = line.strip()
                if line.strip() == "":
                    continue
                if "=" in line:
                    pname, pval = line.split("=", 1)
                    pval = pval.strip("'").strip("\"")
                    envdict[pname.strip()] = pval.strip()

            res["env"] = envdict
            self._state_on_system = res

        return self._state_on_system

    def enableDebug(self):
        self.state.configSetInDictBool("system", "debug", True)
        self.state.configSave()
        self._cache.reset()

    def _initEnv(self):
        """
        init the environment of an executor
        """

        self._env = self.state_on_system["env"]

        self.state_on_system

        print("INITENV")  # TMP
        self.reset()
        j.shell()
        w

        self.config["system"]["container"] = self.state_on_system["iscontainer"]

        if self.isBuildEnv:
            # ONLY RELEVANT FOR BUILDING PYTHON, needs to check what needs to be done (kristof) #TODO:
            j.shell()

        else:
            out = ""
            for key, val in self.dir_paths.items():
                out += "mkdir -p %s\n" % val
            self.execute(out, sudo=True, showout=False)

        self._cache.reset()

        self.config["system"]["executor"] = True
        self.config["DIRS"]["HOMEDIR"] = self.state_on_system["HOME"]
        self.state.configSave()

        if "cfg_state" in self.state_on_system:
            self.state._state = self.state_on_system["cfg_state"]

        self._logger.debug("initenv done on executor base")

    @property
    def platformtype(self):
        return j.core.platformtype.get(self)

    @property
    def cache(self):
        if self._cache is None:
            self._cache = j.core.cache.get("executor" + self.id, reset=True, expiration=600)  # 10 min
        return self._cache

    def file_read(self, path):
        self._logger.debug("file read:%s" % path)
        rc, out, err = self.execute("cat %s" % path, showout=False)
        return out

    def sudo_cmd(self, command):

        if "\n" in command:
            raise RuntimeError(
                "cannot do sudo when multiline script:%s" %
                command)

        if hasattr(self, 'sshclient'):
            login = self.sshclient.config.data['login']
            passwd = self.sshclient.config.data['passwd_']
        else:
            login = getattr(self, 'login', '')
            passwd = getattr(self, 'passwd', '')

        if "darwin" in self.platformtype.osname:
            return command
        if login == 'root':
            return command

        passwd = passwd or "\'\'"

        cmd = 'echo %s | sudo -H -SE -p \'\' bash -c "%s"' % (
            passwd, command.replace('"', '\\"'))
        return cmd

    def file_write(self, path, content, mode=None, owner=None, group=None,
                   append=False, sudo=False, showout=True):
        """
        @param append if append then will add to file

        if file bigger than 100k it will not set the attributes!

        """

        if showout:
            self._logger.debug("file write:%s" % path)

        if len(content) > 100000:
            # when contents are too big, bash will crash
            temp = j.sal.fs.getTempFileName()
            j.sal.fs.writeFile(filename=temp, contents=content,
                               append=False)
            self.upload(temp, path, showout=showout)
            j.sal.fs.remove(temp)
        else:
            content2 = content.encode('utf-8')
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
                cmd += 'chmod %s %s\n' % (mode, path)
            if owner:
                cmd += 'chown %s %s\n' % (owner, path)
            if group:
                cmd += 'chgrp %s %s\n' % (group, path)

            # if sig != self.file_md5(location):
            if sudo and self.type == "ssh":
                self._execute_script(cmd, sudo=sudo, die=True, showout=False)
            else:
                res = self.execute(cmd, sudo=sudo, showout=False)

        self._cache.reset()

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

        # test that it does not do repeating thing & cache works
        for i in range(1000):
            ptype = self.platformtype

        for i in range(1000):
            env = self.env

        prev = None
        for i in range(10000):
            tmp = self.exists("/tmp")
            if prev is not None:
                assert prev == tmp
            prev = tmp

        content = ""
        for i in range(10):
            content += "abcdefg hijklmn %s\n" % i

        contentbig = ""
        for i in range(20000):
            contentbig += "abcdefg hijklmn %s\n" % i

        tmpfile = self.dir_paths["TMPDIR"] + "/testfile"

        self.file_write(tmpfile, content, append=False)
        content2 = self.file_read(tmpfile)

        assert content == content2

        self.file_write(tmpfile, contentbig, append=False)
        content2 = self.file_read(tmpfile)

        assert contentbig == content2

        self._logger.debug("TEST for executor done")
