from Jumpscale import j
import pytoml
import pystache
import base64
import os
try:
    import ujson as json
except ImportError:
    import json


JSBASE = j.application.JSBaseClass


class ExecutorBase(JSBASE):

    def __init__(self, debug=False, checkok=True):
        JSBASE.__init__(self)
        self.debug = debug
        self.checkok = checkok
        self.type = None
        self._id = None
        self._isBuildEnv = None
        self._isSandbox = None
        self.readonly = False
        self.state_disabled = False
        self.CURDIR = ""
        self.reset()

    @property
    def state(self):
        if self._state == None:
            from Jumpscale.core.State import State
            self._state = State(j, executor=self)
        return self._state

    @property
    def config(self):
        return self.state.config

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
        return self.state_on_system["env"]

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

        self.logger.debug(cmds)

        return cmds

    @property
    def prefab(self):
        if self._prefab is None:
            if not getattr(j.tools, "prefab", None):
                # XXX TEMPORARY INCREDIBLY BAD HACK, see issue #50
                from JumpscalePrefab.PrefabFactory \
                    import PrefabRootClassFactory \
                    as _PrefabRootClassFactory
                j.tools.prefab = _PrefabRootClassFactory()

            self._prefab = j.tools.prefab.get(self)
        return self._prefab

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

            self.logger.debug("stateonsystem for non local:%s" % self)
            C = """
            set +ex
            ls "/root/.iscontainer"  > /dev/null 2>&1 && \
                        echo 'ISCONTAINER = 1' || echo 'ISCONTAINER = 0'
                        
                        
            if [ ! -f /tmp/uid.txt ]; then
                echo $RANDOM > /tmp/uid.txt
            fi
            echo UID = `cat /tmp/uid.txt`                    
                                                            
            echo UNAME = \""$(uname -mnprs)"\"
        
            
            echo "HOME = $HOME"
            #TODO:*1 check if it exists if not fall back on /root
            
            echo HOSTNAME = "$(hostname)"
            
            lsmod > /dev/null 2>&1|grep vboxdrv |grep -v grep  > \
                        /dev/null 2>&1 && echo 'VBOXDRV=1' || echo 'VBOXDRV=0'
            
            #OS
            apt-get -v > /dev/null 2>&1 && echo 'OS_TYPE="ubuntu"'
            test -f /etc/arch-release > /dev/null 2>&1 && echo 'OS_TYPE="arch"'
            test -f /etc/redhat-release > /dev/null 2>&1 && echo 'OS_TYPE="redhat"'
            apk -v > /dev/null 2>&1 && echo 'OS_TYPE="alpine"'
            brew -v > /dev/null 2>&1 && echo 'OS_TYPE="darwin"'
            opkg -v > /dev/null 2>&1 && echo 'OS_TYPE="LEDE"'
            cat /etc/os-release | grep "VERSION_ID"
            
                                 
            echo "CFG_JUMPSCALE = --TEXT--"
            #NEEDS TO CORRESPOND WITH jsconfig_path in main __init__.py file
            cat $HOME/opt/cfg/jumpscale.toml 2>/dev/null || echo ""
            echo --TEXT--

            echo "CFG_JUMPSCALE2 = --TEXT--"
            #NEEDS TO CORRESPOND WITH jsconfig_path in main __init__.py file
            cat /sandbox/cfg/jumpscale.toml 2>/dev/null || echo ""
            echo --TEXT--


            echo "CFG_STATE = --TEXT--"
            cat $HOME/opt/cfg/state.toml 2>/dev/null || echo ""
            echo --TEXT--
                        
            echo "BASHPROFILE = --TEXT--"
            cat $HOME/.profile_js 2>/dev/null || echo ""
            echo --TEXT--
            
            echo "ENV = --TEXT--"
            export
            echo --TEXT--
            """
            C = j.core.text.strip(C)
            rc, out, err = self.execute(C, showout=False, sudo=False)
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

            if res["cfg_jumpscale2"].strip() != "" and os.path.exists(res["cfg_jumpscale2"]):
                res["cfg_jumpscale"] = res["cfg_jumpscale2"]

            if res["cfg_jumpscale"].strip() != "":
                try:
                    res["cfg_jumpscale"] = pytoml.loads(res["cfg_jumpscale"])
                except Exception as e:
                    raise RuntimeError(
                        "Could not load jumpscale config file "
                        "(pytoml error)\n%s\n" %
                        res["cfg_jumpscale"])
            else:
                res["cfg_jumpscale"] = {}

            if res["cfg_state"].strip() != "":
                try:
                    res["cfg_state"] = pytoml.loads(res["cfg_state"])
                except Exception as e:
                    raise RuntimeError(
                        "Could not load state file "
                        "(pytoml error)\n%s\n" %
                        res["cfg_state"])
            else:
                res["cfg_state"] = {}

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
        self.cache.reset()



    def initEnv(self):
        """
        init the environment of an executor
        """
        print("INITENV") #TMP
        self.reset()

        self.config["system"]["container"] = self.state_on_system["iscontainer"]

        if self.isBuildEnv:
            #ONLY RELEVANT FOR BUILDING PYTHON, needs to check what needs to be done (kristof) #TODO:
            j.shell()
            for key, val in DIRPATHS.items():
                j.sal.fs.createDir(val)
            githubpath="%s/github/threefoldtech"%DIRPATHS["CODEDIR"]

            #link code dir from host to build dir if it exists
            if not j.sal.fs.exists(githubpath):
                sdir1 = "%s/code/github/threefoldtech"%os.environ["HOME"]
                sdir2 = "/opt/code/github/threefoldtech"
                if j.sal.fs.exists(sdir1):
                    sdir = sdir1
                elif j.sal.fs.exists(sdir2):
                    sdir = sdir2
                else:
                    sdir = None
                if sdir is not None:
                    j.sal.fs.symlink(sdir, githubpath, overwriteTarget=True)

        else:
            out = ""
            for key, val in self.dir_paths.items():
                out += "mkdir -p %s\n" % val
            self.execute(out, sudo=True,showout=False)

        self.cache.reset()

        self.config["system"]["executor"]=True
        # self.config["DIRS"]["HOMEDIR"] = self.state_on_system["HOME"]
        self.state.configSave()

        # if "cfg_state" in self.state_on_system:
        #     self.state._state = self.state_on_system["cfg_state"]

        self.logger.debug("initenv done on executor base")

    def env_check_init(self):
        """ check that system has been initialise, if not, do so
        """
        if "executor" not in self.config["system"]:
            #means we did not initialize an executor
            self.initEnv()

    @property
    def dir_paths(self):
        return self.state.configGet('dirs')

    @property
    def platformtype(self):
        return j.core.platformtype.get(self)

    @property
    def cache(self):
        if self._cache is None:
            self._cache = j.core.cache.get("executor" + self.id, reset=True, expiration=600)  # 10 min
        return self._cache


    def file_read(self, path):
        self.logger.debug("file read:%s" % path)
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
            self.logger.debug("file write:%s" % path)

        if len(content) > 100000:
            # when contents are too big, bash will crash
            temp = j.sal.fs.getTempFileName()
            j.sal.fs.writeFile(filename=temp, contents=content,
                                    append=False)
            self.upload(temp, path,showout=showout)
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

        self.cache.reset()

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

        self.logger.debug("TEST for executor done")