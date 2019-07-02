from __future__ import unicode_literals
import copy
import getpass

DEFAULTBRANCH = ["development", "development_installer"]

import socket
import grp
import os
import random
import select
import shutil
import stat
import subprocess
import sys
import textwrap
import time
import re
from fcntl import F_GETFL, F_SETFL, fcntl
from os import O_NONBLOCK, read
from pathlib import Path
from subprocess import Popen, check_output
import inspect

try:
    import json
except:
    pass

try:
    import traceback
except:
    traceback = None

try:
    import pudb
except:
    pudb = None

try:
    import pygments
except Exception as e:
    pygments = None

if pygments:
    from pygments import formatters
    from pygments import lexers

    pygments_formatter = formatters.get_formatter_by_name("terminal")
    pygments_pylexer = lexers.get_lexer_by_name("python")
else:
    pygments_formatter = False
    pygments_pylexer = False


class BaseInstallerror(Exception):
    pass


class InputError(Exception):
    pass
    # def __init__(self, expression, message):
    #     self.expression = expression
    #     self.message = message


def my_excepthook(exception_type, exception_obj, tb):
    try:
        Tools.log(msg=exception_obj, tb=tb, level=40)
    except:
        print(exception_obj)
    if MyEnv.debug and traceback and pudb:
        # exception_type, exception_obj, tb = sys.exc_info()
        pudb.post_mortem(tb)
    Tools.pprint("{RED}CANNOT CONTINUE{RESET}")
    sys.exit(1)


import inspect

try:
    import yaml

    def serializer(data):
        return yaml.dump(data, default_flow_style=False, default_style="", indent=4, line_break="\n")


except:
    try:
        import json

        def serializer(data):
            return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=True)

    except:

        def serializer(data):
            return str(data)


class RedisTools:
    @staticmethod
    def client_core_get(
        addr="localhost", port=6379, unix_socket_path="/sandbox/var/redis.sock", die=True, fake_ok=True
    ):
        """

        :param addr:
        :param port:
        :param unix_socket_path:
        :param die: if cannot find fake or real die
        :param fake_ok: can return a fake redis connection which will go to memory only
        :return:
        """

        RedisTools.unix_socket_path = unix_socket_path

        try:
            import redis
        except ImportError:
            if fake_ok:
                try:
                    import fakeredis

                    res = fakeredis.FakeStrictRedis()
                    res.fake = True
                    return res
                except ImportError:
                    # dit not find fakeredis so can only return None
                    if die:
                        raise RuntimeError(
                            "cannot connect to fakeredis, could not import the library, please install fakeredis"
                        )
                    return None
            else:
                if die:
                    raise RuntimeError("redis python lib not installed, do pip3 install redis")
                return None

        try:
            cl = Redis(unix_socket_path=unix_socket_path, db=0)
            cl.fake = False
            assert cl.ping()
        except Exception as e:
            cl = None
            if addr == "" and die:
                raise e
        else:
            return cl

        try:
            cl = Redis(host=addr, port=port, db=0)
            cl.fake = False
            assert cl.ping()
        except Exception as e:
            if die:
                raise e
            cl = None

        return cl

    @staticmethod
    def core_get(reset=False, tcp=True):
        """

        kosmos 'j.clients.redis.core_get(reset=False)'

        will try to create redis connection to {DIR_TEMP}/redis.sock or /sandbox/var/redis.sock  if sandbox
        if that doesn't work then will look for std redis port
        if that does not work then will return None


        :param tcp, if True then will also start tcp port on localhost on 6379


        :param reset: stop redis, defaults to False
        :type reset: bool, optional
        :raises RuntimeError: redis couldn't be started
        :return: redis instance
        :rtype: Redis
        """

        if reset:
            RedisTools.core_stop()

        MyEnv.init()

        if MyEnv.db and MyEnv.db.ping() and MyEnv.db.fake is False:
            return MyEnv.db

        if not RedisTools.core_running(tcp=tcp):
            RedisTools._core_start(tcp=tcp)

        MyEnv.db = RedisTools.client_core_get()

        try:
            from Jumpscale import j

            j.core.db = MyEnv.db
        except:
            pass

        return MyEnv.db

    @staticmethod
    def core_stop():
        """
        kill core redis

        :raises RuntimeError: redis wouldn't be stopped
        :return: True if redis is not running
        :rtype: bool
        """
        MyEnv.db = None
        Tools.execute("redis-cli -s %s shutdown" % RedisTools.unix_socket_path, die=False, showout=False)
        Tools.execute("redis-cli shutdown", die=False, showout=False)
        nr = 0
        while True:
            if not RedisTools.core_running():
                return True
            if nr > 200:
                raise RuntimeError("could not stop redis")
            time.sleep(0.05)

    def core_running(unixsocket=True, tcp=True):

        """
        Get status of redis whether it is currently running or not

        :raises e: did not answer
        :return: True if redis is running, False if redis is not running
        :rtype: bool
        """
        if unixsocket:
            r = RedisTools.client_core_get(fake_ok=False, die=False)
            if r:
                return True

        if tcp and Tools.tcp_port_connection_test("localhost", 6379):
            r = RedisTools.client_core_get(ipaddr="localhost", port=6379, fake_ok=False, die=False)
            if r:
                return True

        return False

    def _core_start(tcp=True, timeout=20, reset=False):

        """
        kosmos "j.clients.redis.core_get(reset=True)"

        installs and starts a redis instance in separate ProcessLookupError
        when not in sandbox:
                standard on {DIR_TEMP}/redis.sock
        in sandbox will run in:
            /sandbox/var/redis.sock

        :param timeout:  defaults to 20
        :type timeout: int, optional
        :param reset: reset redis, defaults to False
        :type reset: bool, optional
        :raises RuntimeError: redis server not found after install
        :raises RuntimeError: platform not supported for start redis
        :raises j.exceptions.Timeout: Couldn't start redis server
        :return: redis instance
        :rtype: Redis
        """

        if reset == False:
            if RedisTools.core_running(tcp=tcp):
                return RedisTools.core_get()

            if MyEnv.platform_is_osx:
                if not Tools.cmd_installed("redis-server"):
                    # prefab.system.package.install('redis')
                    Tools.execute("brew unlink redis", die=False)
                    Tools.execute("brew install redis")
                    Tools.execute("brew link redis")
                    if not Tools.cmd_installed("redis-server"):
                        raise RuntimeError("Cannot find redis-server even after install")
                Tools.execute("redis-cli -s {DIR_TMP}/redis.sock shutdown", die=False, showout=False)
                Tools.execute("redis-cli -s %s shutdown" % RedisTools.unix_socket_path, die=False, showout=False)
                Tools.execute("redis-cli shutdown", die=False, showout=False)
            elif MyEnv.platform_is_linux:
                Tools.execute("apt install redis-server -y")
            else:
                raise RuntimeError("platform not supported for start redis")

        if not MyEnv.platform_is_osx:
            cmd = "sysctl vm.overcommit_memory=1"
            os.system(cmd)

        if reset:
            RedisTools.core_stop()

        cmd = (
            "mkdir -p /sandbox/var;redis-server --unixsocket $UNIXSOCKET "
            "--port 6379 "
            "--maxmemory 100000000 --daemonize yes"
        )
        cmd = cmd.replace("$UNIXSOCKET", RedisTools.unix_socket_path)

        Tools.log(cmd)
        Tools.execute(cmd)
        limit_timeout = time.time() + timeout
        while time.time() < limit_timeout:
            if RedisTools.core_running():
                break
            print(1)
            time.sleep(0.1)
        else:
            raise RuntimeError("Couldn't start redis server")


try:
    import redis
except:
    redis = False

if redis:

    class RedisQueue:
        def __init__(self, redis, key):
            self.__db = redis
            self.key = key
            self.empty = False

        def qsize(self):
            """Return the approximate size of the queue.

            :return: approximate size of queue
            :rtype: int
            """
            return self.__db.llen(self.key)

        @property
        def empty(self):
            """Return True if the queue is empty, False otherwise."""
            return self.qsize() == 0

        def reset(self):
            """
            make empty
            :return:
            """
            while self.empty == False:
                if self.get_nowait() == None:
                    self.empty = True

        def put(self, item):
            """Put item into the queue."""
            self.__db.rpush(self.key, item)

        def get(self, timeout=20):
            """Remove and return an item from the queue."""
            if timeout > 0:
                item = self.__db.blpop(self.key, timeout=timeout)
                if item:
                    item = item[1]
            else:
                item = self.__db.lpop(self.key)
            return item

        def fetch(self, block=True, timeout=None):
            """Return an item from the queue without removing"""
            if block:
                item = self.__db.brpoplpush(self.key, self.key, timeout)
            else:
                item = self.__db.lindex(self.key, 0)
            return item

        def set_expire(self, time):
            self.__db.expire(self.key, time)

        def get_nowait(self):
            """Equivalent to get(False)."""
            return self.get(False)

    class Redis(redis.Redis):

        _storedprocedures_to_sha = {}
        _redis_cli_path_ = None

        def __init__(self, *args, **kwargs):
            redis.Redis.__init__(self, *args, **kwargs)
            self._storedprocedures_to_sha = {}

        # def dict_get(self, key):
        #     return RedisDict(self, key)

        def queue_get(self, key):
            """get redis queue
            """
            return RedisQueue(self, key)

        def storedprocedure_register(self, name, nrkeys, path_or_content):
            """create stored procedure from path

            :param path: the path where the stored procedure exist
            :type path_or_content: str which is the lua content or the path
            :raises Exception: when we can not find the stored procedure on the path

            will return the sha

            to use the stored procedure do

            redisclient.evalsha(sha,3,"a","b","c")  3 is for nr of keys, then the args

            the stored procedure can be found in hset storedprocedures:$name has inside a json with

            is json encoded dict
             - script: ...
             - sha: ...
             - nrkeys: ...

            there is also storedprocedures:sha -> sha without having to decode json

            tips on lua in redis:
            https://redis.io/commands/eval

            """

            if "\n" not in path_or_content:
                f = open(path_or_content, "r")
                lua = f.read()
                path = path_or_content
            else:
                lua = path_or_content
                path = ""

            script = self.register_script(lua)

            dd = {}
            dd["sha"] = script.sha
            dd["script"] = lua
            dd["nrkeys"] = nrkeys
            dd["path"] = path

            data = json.dumps(dd)

            self.hset("storedprocedures:data", name, data)
            self.hset("storedprocedures:sha", name, script.sha)

            self._storedprocedures_to_sha = {}

            return script

        def storedprocedure_delete(self, name):
            self.hdel("storedprocedures:data", name)
            self.hdel("storedprocedures:sha", name)
            self._storedprocedures_to_sha = {}

        @property
        def _redis_cli_path(self):
            if not self.__class__._redis_cli_path_:
                if Tools.cmd_installed("redis-cli_"):
                    self.__class__._redis_cli_path_ = "redis-cli_"
                else:
                    self.__class__._redis_cli_path_ = "redis-cli"
            return self.__class__._redis_cli_path_

        def redis_cmd_execute(self, command, debug=False, debugsync=False, keys=[], args=[]):
            """

            :param command:
            :param args:
            :return:
            """
            rediscmd = self._redis_cli_path
            if debug:
                rediscmd += " --ldb"
            elif debugsync:
                rediscmd += " --ldb-sync-mode"
            rediscmd += " --%s" % command
            for key in keys:
                rediscmd += " %s" % key
            if len(args) > 0:
                rediscmd += " , "
                for arg in args:
                    rediscmd += " %s" % arg
            # print(rediscmd)
            _, out, _ = Tools.execute(rediscmd, interactive=True)
            return out

        def _sp_data(self, name):
            if name not in self._storedprocedures_to_sha:
                data = self.hget("storedprocedures:data", name)
                if not data:
                    raise RuntimeError("could not find: '%s:%s' in redis" % (("storedprocedures:data", name)))
                data2 = json.loads(data)
                self._storedprocedures_to_sha[name] = data2
            return self._storedprocedures_to_sha[name]

        def storedprocedure_execute(self, name, *args):
            """

            :param name:
            :param args:
            :return:
            """

            data = self._sp_data(name)
            sha = data["sha"]  # .encode()
            assert isinstance(sha, (str))
            # assert isinstance(sha, (bytes, bytearray))
            Tools.shell()
            return self.evalsha(sha, data["nrkeys"], *args)
            # self.eval(data["script"],data["nrkeys"],*args)
            # return self.execute_command("EVALSHA",sha,data["nrkeys"],*args)

        def storedprocedure_debug(self, name, *args):
            """
            to see how to use the debugger see https://redis.io/topics/ldb

            to break put: redis.breakpoint() inside your lua code
            to continue: do 'c'


            :param name: name of the sp to execute
            :param args: args to it
            :return:
            """
            data = self._sp_data(name)
            path = data["path"]
            if path == "":
                from pudb import set_trace

                set_trace()

            nrkeys = data["nrkeys"]
            args2 = args[nrkeys:]
            keys = args[:nrkeys]

            out = self.redis_cmd_execute("eval %s" % path, debug=True, keys=keys, args=args2)

            return out


class Tools:

    _supported_editors = ["micro", "mcedit", "joe", "vim", "vi"]  # DONT DO AS SET  OR ITS SORTED
    j = None
    _shell = None

    @staticmethod
    def traceback_text_get(tb=None, stdout=False):
        """
        format traceback to readable text
        :param tb:
        :return:
        """
        if tb is None:
            tb = sys.last_traceback
        out = ""
        for item in traceback.extract_tb(tb):
            fname = item.filename
            if len(fname) > 60:
                fname = fname[-60:]
            line = "%-60s : %-4s: %s" % (fname, item.lineno, item.line)
            if stdout:
                line2 = "        {GRAY}%-60s :{RESET} %-4s: " % (fname, item.lineno)
                Tools.pprint(line2, end="", log=False)
                if pygments_formatter is not False:
                    print(pygments.highlight(item.line, pygments_pylexer, pygments_formatter).rstrip())
                else:
                    Tools.pprint(item.line, log=False)

            out += "%s\n" % line
        return out

    @staticmethod
    def log(
        msg, cat="", level=10, data=None, context=None, _deeper=False, stdout=True, redis=True, tb=None, data_show=True
    ):
        """

        :param msg:
        :param level:
            - CRITICAL 	50
            - ERROR 	40
            - WARNING 	30
            - INFO 	    20
            - STDOUT 	15
            - DEBUG 	10

        :return:
        """
        if isinstance(msg, Exception):
            Tools.pprint("\n\n{BOLD}{RED}EXCEPTION{RESET}\n")
            msg = "{RED}EXCEPTION: {RESET}%s" % str(msg)
            level = 50
            if cat is "":
                cat = "exception"
        if tb:
            if tb.tb_next is not None:
                frame_ = tb.tb_next.tb_frame
            else:
                # extype, value, tb = sys.exc_info()
                frame_ = tb.tb_frame
            if data is None:
                data = Tools.traceback_text_get(tb, stdout=True)
                data_show = False
            else:
                msg += "\n%s" % Tools.traceback_text_get(tb, stdout=True)
            print()
        else:
            if _deeper:
                frame_ = inspect.currentframe().f_back
            else:
                frame_ = inspect.currentframe().f_back.f_back

        fname = frame_.f_code.co_filename.split("/")[-1]
        defname = frame_.f_code.co_name
        linenr = frame_.f_code.co_firstlineno

        logdict = {}
        logdict["linenr"] = linenr
        logdict["processid"] = MyEnv.appname
        logdict["message"] = msg
        logdict["filepath"] = fname
        logdict["level"] = level
        if context:
            logdict["context"] = context
        else:
            logdict["context"] = defname
        logdict["cat"] = cat

        if data and isinstance(data, dict):
            if "password" in data or "secret" in data or "passwd" in data:
                data["password"] = "***"

        logdict["data"] = data

        if stdout:
            Tools.log2stdout(logdict, data_show=data_show)

    # @staticmethod
    # def error_raise(msg, pythonerror=None):
    #     print ("** ERROR **")
    #     Tools.log(msg)
    #     if MyEnv.debug and traceback and pudb:
    #         extype, value, tb = sys.exc_info()
    #         if tb is not None:
    #             traceback.print_exc()
    #             pudb.post_mortem(tb,e_value=pythonerror)
    #         else:
    #             from pudb import set_trace
    #             set_trace()
    #         sys.exit(1)
    #     raise RuntimeError(msg)

    @staticmethod
    def _execute_interactive(cmd=None, args=None, die=True, original_command=None):

        if args is None:
            args = cmd.split(" ")
        # else:
        #     args[0] = shutil.which(args[0])

        returncode = os.spawnlp(os.P_WAIT, args[0], *args)
        cmd = " ".join(args)
        if returncode == 127:
            raise RuntimeError("{}: command not found\n".format(cmd))
        if returncode > 0 and returncode != 999:
            if die:
                if original_command:
                    raise RuntimeError(
                        "***ERROR EXECUTE INTERACTIVE:\nCould not execute:%s\nreturncode:%s\n"
                        % (original_command, returncode)
                    )
                else:
                    raise RuntimeError(
                        "***ERROR EXECUTE INTERACTIVE:\nCould not execute:%s\nreturncode:%s\n" % (cmd, returncode)
                    )
            return returncode, "", ""
        return returncode, "", ""

    @staticmethod
    def file_touch(path):
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)

        with open(path, "a"):
            os.utime(path, None)

    @staticmethod
    def file_edit(path):
        """
        starts the editor micro with file specified
        """
        user_editor = os.environ.get("EDITOR")
        if user_editor and Tools.cmd_installed(user_editor):
            Tools._execute_interactive("%s %s" % (user_editor, path))
            return
        for editor in Tools._supported_editors:
            if Tools.cmd_installed(editor):
                Tools._execute_interactive("%s %s" % (editor, path))
                return
        raise RuntimeError("cannot edit the file: '{}', non of the supported editors is installed".format(path))

    @staticmethod
    def file_write(path, content, replace=False, args=None):
        if args is None:
            args = {}
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)
        p = Path(path)
        if replace:
            content = Tools.text_replace(content, args=args)
        p.write_text(content)

    @staticmethod
    def file_text_read(path):
        path = Tools.text_replace(path)
        p = Path(path)
        try:
            return p.read_text()
        except Exception as e:
            Tools.shell()

    @staticmethod
    def dir_ensure(path, remove_existing=False):
        """Ensure the existance of a directory on the system, if the
        Directory does not exist, it will create

        :param path:path of the directory
        :type path: string
        :param remove_existing: If True and the path already exist,
            the existing path will be removed first, defaults to False
        :type remove_existing: bool, optional
        """

        path = Tools.text_replace(path)

        if os.path.exists(path) and remove_existing is True:
            Tools.delete(path)
        elif os.path.exists(path):
            return
        os.makedirs(path)

    @staticmethod
    def link(src, dest, chmod=None):
        """

        :param src: is where the link goes to
        :param dest: is where he link will be
        :param chmod e.g. 770
        :return:
        """
        src = Tools.text_replace(src)
        dest = Tools.text_replace(dest)
        Tools.execute("rm -f %s" % dest)
        Tools.execute("ln -s {} {}".format(src, dest))
        if chmod:
            Tools.execute("chmod %s %s" % (chmod, dest))

    @staticmethod
    def delete(path):
        """Remove a File/Dir/...
        @param path: string (File path required to be removed)
        """
        path = Tools.text_replace(path)
        if MyEnv.debug:
            Tools.log("Remove file with path: %s" % path)
        if os.path.islink(path):
            os.unlink(path)
        if not Tools.exists(path):
            return

        mode = os.stat(path).st_mode
        if os.path.isfile(path) or stat.S_ISSOCK(mode):
            if len(path) > 0 and path[-1] == os.sep:
                path = path[:-1]
            os.remove(path)
        else:
            shutil.rmtree(path)

    @staticmethod
    def path_parent(path):
        """
        Returns the parent of the path:
        /dir1/dir2/file_or_dir -> /dir1/dir2/
        /dir1/dir2/            -> /dir1/
        """
        parts = path.split(os.sep)
        if parts[-1] == "":
            parts = parts[:-1]
        parts = parts[:-1]
        if parts == [""]:
            return os.sep
        return os.sep.join(parts)

    @staticmethod
    def exists(path, followlinks=True):
        """Check if the specified path exists
        @param path: string
        @rtype: boolean (True if path refers to an existing path)
        """
        if path is None:
            raise TypeError("Path is not passed in system.fs.exists")
        found = False
        try:
            st = os.lstat(path)
            found = True
        except (OSError, AttributeError):
            pass
        if found and followlinks and stat.S_ISLNK(st.st_mode):
            if MyEnv.debug:
                Tools.log("path %s exists" % str(path.encode("utf-8")))
            linkpath = os.readlink(path)
            if linkpath[0] != "/":
                linkpath = os.path.join(Tools.path_parent(path), linkpath)
            return Tools.exists(linkpath)
        if found:
            return True
        # Tools.log('path %s does not exist' % str(path.encode("utf-8")))
        return False

    @staticmethod
    def _installbase_for_shell():

        if "darwin" in MyEnv.platform():

            script = """
            pip3 install ipython==6.5.0
            """
            Tools.execute(script, interactive=True)

        else:

            script = """
                #if ! grep -Fq "deb http://mirror.unix-solutions.be/ubuntu/ bionic" /etc/apt/sources.list; then
                #    echo >> /etc/apt/sources.list
                #    echo "# Jumpscale Setup" >> /etc/apt/sources.list
                #    echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
                #fi
                sudo apt-get update
                sudo apt-get install -y python3-pip
                sudo apt-get install -y locales
                sudo apt-get install -y curl rsync
                sudo apt-get install -y unzip
                pip3 install ipython==6.5.0
                pip3 install pudb
                pip3 install pygments
                locale-gen --purge en_US.UTF-8
            """
            Tools.execute(script, interactive=True)

    @staticmethod
    def clear():
        print(chr(27) + "[2j")
        print("\033c")
        print("\x1bc")

    @staticmethod
    def shell(loc=True):
        if loc:
            import inspect

            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            f = calframe[1]
        else:
            f = None
        if Tools._shell is None:

            try:
                from IPython.terminal.embed import InteractiveShellEmbed
            except Exception as e:
                Tools._installbase_for_shell()
                from IPython.terminal.embed import InteractiveShellEmbed
            if f:
                print("\n*** file: %s" % f.filename)
                print("*** function: %s [linenr:%s]\n" % (f.function, f.lineno))

            Tools._shell = InteractiveShellEmbed(banner1="", exit_msg="")
            Tools._shell.Completer.use_jedi = False
        return Tools._shell(stack_depth=2)

    # @staticmethod
    # def shell(loc=True,exit=True):
    #     if loc:
    #         import inspect
    #         curframe = inspect.currentframe()
    #         calframe = inspect.getouterframes(curframe, 2)
    #         f = calframe[1]
    #         print("\n*** file: %s"%f.filename)
    #         print("*** function: %s [linenr:%s]\n" % (f.function,f.lineno))
    #     from ptpython.repl import embed
    #     Tools.clear()
    #     history_filename="~/.jsx_history"
    #     if not Tools.exists(history_filename):
    #         Tools.file_write(history_filename,"")
    #     ptconfig = None
    #     if exit:
    #         sys.exit(embed(globals(), locals(),configure=ptconfig,history_filename=history_filename))
    #     else:
    #         embed(globals(), locals(),configure=ptconfig,history_filename=history_filename)

    @staticmethod
    def text_strip(content, ignorecomments=False, args={}, replace=False, executor=None, colors=True):
        """
        remove all spaces at beginning & end of line when relevant (this to allow easy definition of scripts)
        args will be substitued to .format(...) string function https://docs.python.org/3/library/string.html#formatspec
        MyEnv.config will also be given to the format function


        for examples see text_replace method


        """
        # find generic prepend for full file
        minchars = 9999
        prechars = 0
        for line in content.split("\n"):
            if line.strip() == "":
                continue
            if ignorecomments:
                if line.strip().startswith("#") and not line.strip().startswith("#!"):
                    continue
            prechars = len(line) - len(line.lstrip())
            # Tools.log ("'%s':%s:%s"%(line,prechars,minchars))
            if prechars < minchars:
                minchars = prechars

        if minchars > 0:

            # if first line is empty, remove
            lines = content.split("\n")
            if len(lines) > 0:
                if lines[0].strip() == "":
                    lines.pop(0)
            content = "\n".join(lines)

            # remove the prechars
            content = "\n".join([line[minchars:] for line in content.split("\n")])

        if replace:
            content = Tools.text_replace(content=content, args=args, executor=executor, text_strip=False)
        else:
            if colors and "{" in content:
                for key, val in MyEnv.MYCOLORS.items():
                    content = content.replace("{%s}" % key, val)

        return content

    @staticmethod
    def text_replace(content, args=None, executor=None, ignorecomments=False, text_strip=True, ignore_error=False):
        """

        Tools.text_replace

        args will be substitued to .format(...) string function https://docs.python.org/3/library/string.html#formatspec
        MyEnv.config will also be given to the format function

        content example:

        "{name!s:>10} {val} {n:<10.2f}"  #floating point rounded to 2 decimals

        performance is +100k per sec

        will call the strip if

        following colors will be replaced e.g. use {RED} to get red color.

        MYCOLORS =
                "RED",
                "BLUE",
                "CYAN",
                "GREEN",
                "YELLOW,
                "RESET",
                "BOLD",
                "REVERSE"

        """

        class format_dict(dict):
            def __missing__(self, key):
                return "{%s}" % key

        if args is None:
            args = {}
        else:
            args = copy.copy(args)  # make sure we don't change the original

        if "{" in content:

            if args is None:
                args = {}

            if executor:
                args.update(executor.config)
            else:
                for key, val in MyEnv.config.items():
                    if key not in args:
                        args[key] = val

            args.update(MyEnv.MYCOLORS)

            replace_args = format_dict(args)
            try:
                content = content.format_map(replace_args)
            except ValueError as e:
                if ignore_error:
                    pass  # e.g. if { is
                else:
                    sorted = [i for i in args.keys()]
                    # raise RuntimeError("could not replace \n%s \nin \n%s" % (sorted, content))
            if not ignore_error:
                if "{" in content:
                    try:
                        content = content.format_map(replace_args)  # this to deal with nested {
                    except ValueError as e:
                        sorted = [i for i in args.keys()]
                        raise RuntimeError(
                            "could not replace \n%s \nin \n%s\n, remaining {, if you want to ignore the error use ignore_error=True"
                            % (sorted, content)
                        )

        if text_strip:
            content = Tools.text_strip(content, ignorecomments=ignorecomments, replace=False)

        return content

    @staticmethod
    def log2stdout(logdict, data_show=True):
        """

        :param logdict:

            logdict["linenr"]
            logdict["processid"]
            logdict["message"]
            logdict["filepath"]
            logdict["level"]
            logdict["context"]
            logdict["cat"]
            logdict["data"]
            logdict["epoch"]

        :return:
        """

        if "epoch" in logdict:
            timetuple = time.localtime(logdict["epoch"])
        else:
            timetuple = time.localtime(time.time())
        logdict["TIME"] = time.strftime(MyEnv.FORMAT_TIME, timetuple)

        if logdict["level"] < 11:
            LOGCAT = "DEBUG"
        elif logdict["level"] == 15:
            LOGCAT = "STDOUT"
        elif logdict["level"] < 21:
            LOGCAT = "INFO"
        elif logdict["level"] < 31:
            LOGCAT = "WARNING"
        elif logdict["level"] < 41:
            LOGCAT = "ERROR"
        else:
            LOGCAT = "CRITICAL"

        LOGFORMAT = MyEnv.LOGFORMAT[LOGCAT]

        logdict.update(MyEnv.MYCOLORS)

        if len(logdict["filepath"]) > 16:
            logdict["filename"] = logdict["filepath"][len(logdict["filepath"]) - 18 :]
        else:
            logdict["filename"] = logdict["filepath"]

        if len(logdict["context"]) > 35:
            logdict["context"] = logdict["context"][len(logdict["context"]) - 34 :]
        if logdict["context"].startswith("_"):
            logdict["context"] = ""
        elif logdict["context"].startswith(":"):
            logdict["context"] = ""

        p = print
        if MyEnv.config['DEBUG'] and MyEnv.config.get('log_printer'):
            p = MyEnv.config['log_printer']

        msg = Tools.text_replace(LOGFORMAT, args=logdict, ignore_error=True)
        msg = Tools.text_replace(msg, args=logdict, ignore_error=True)
        p(msg)

        if data_show:
            if logdict["data"] not in ["", None, {}]:
                if isinstance(logdict["data"], dict):
                    try:
                        data = serializer(logdict["data"])
                    except Exception as e:
                        data = logdict["data"]
                else:
                    data = logdict["data"]
                data = Tools.text_indent(data, 10, strip=True)
                try:
                    data = Tools.text_replace(data, ignore_error=True, text_strip=False)
                except:
                    pass
                p(data.rstrip())

    @staticmethod
    def pprint(content, ignorecomments=False, text_strip=False, args=None, colors=False, indent=0, end="\n", log=True):
        """

        :param content: what to print
        :param ignorecomments: ignore #... on line
        :param text_strip: remove spaces at start of line
        :param args: replace args {} is template construct
        :param colors:
        :param indent:


        MYCOLORS =
                "RED",
                "BLUE",
                "CYAN",
                "GREEN",
                "RESET",
                "BOLD",
                "REVERSE"

        """

        if args or colors or text_strip:
            content = Tools.text_replace(
                content, args=args, text_strip=text_strip, ignorecomments=ignorecomments, ignore_error=True
            )
        elif content.find("{RESET}") != -1:
            for key, val in MyEnv.MYCOLORS.items():
                content = content.replace("{%s}" % key, val)

        if indent > 0:
            content = Tools.text_indent(content)
        if log:
            Tools.log(content, level=15, stdout=False)
        print(content, end=end)

    @staticmethod
    def text_md5(txt):
        import hashlib

        if isinstance(s, str):
            s = s.encode("utf-8")
        impl = hashlib.new("md5", data=s)
        return impl.hexdigest()

    @staticmethod
    def text_indent(content, nspaces=4, wrap=180, strip=True, indentchar=" ", args=None):
        """Indent a string a given number of spaces.

        Parameters
        ----------

        instr : basestring
            The string to be indented.
        nspaces : int (default: 4)
            The number of spaces to be indented.

        Returns
        -------

        str|unicode : string indented by ntabs and nspaces.

        """
        if content is None:
            raise RuntimeError("content cannot be None")
        content = str(content)
        if args is not None:
            content = Tools.text_replace(content, args=args)
        if strip:
            content = Tools.text_strip(content, replace=False)
        if wrap > 0:
            content = Tools.text_wrap(content, wrap)

            # flatten = True
        ind = indentchar * nspaces
        out = ""
        for line in content.split("\n"):
            out += "%s%s\n" % (ind, line)
        return out

    @staticmethod
    def text_wrap(txt, length=120):
        out = ""
        for line in txt.split("\n"):
            out += textwrap.fill(line, length, subsequent_indent="    ") + "\n"
        return out

    @staticmethod
    def _file_path_tmp_get(ext="sh"):
        ext = ext.strip(".")
        return Tools.text_replace("/tmp/jumpscale/scripts/{RANDOM}.{ext}", args={"RANDOM": Tools._random(), "ext": ext})

    @staticmethod
    def _random():
        return str(random.getrandbits(16))

    @staticmethod
    def execute(
        command,
        showout=True,
        useShell=True,
        cwd=None,
        timeout=800,
        die=True,
        async_=False,
        args=None,
        env=None,
        interactive=False,
        self=None,
        replace=True,
        asfile=False,
        original_command=None,
        log=False,
    ):

        if env is None:
            env = {}
        if self is None:
            self = MyEnv
        command = Tools.text_strip(command, args=args, replace=replace)
        if "\n" in command or asfile:
            path = Tools._file_path_tmp_get()
            if MyEnv.debug or log:
                Tools.log("execbash:\n'''%s\n%s'''\n" % (path, command))
            command2 = ""
            if die:
                command2 = "set -e\n"
            if cwd:
                command2 += "cd %s\n" % cwd
            command2 += command
            Tools.file_write(path, command2)
            # print(command2)
            command3 = "bash %s" % path
            res = Tools.execute(
                command3,
                showout=showout,
                useShell=useShell,
                cwd=cwd,
                timeout=timeout,
                die=die,
                env=env,
                self=self,
                interactive=interactive,
                asfile=False,
                original_command=command,
            )
            Tools.delete(path)
            return res
        else:

            if interactive:
                res = Tools._execute_interactive(cmd=command, die=die, original_command=original_command)
                if MyEnv.debug or log:
                    Tools.log("execute interactive:%s" % command)
                return res
            else:
                if MyEnv.debug or log:
                    Tools.log("execute:%s" % command)

            os.environ["PYTHONUNBUFFERED"] = "1"  # WHY THIS???

            # if hasattr(subprocess, "_mswindows"):
            #     mswindows = subprocess._mswindows
            # else:
            #     mswindows = subprocess.mswindows

            if env == None or env == {}:
                env = os.environ

            if useShell:
                p = Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    close_fds=MyEnv.platform_is_unix,
                    shell=True,
                    universal_newlines=False,
                    cwd=cwd,
                    bufsize=0,
                    executable="/bin/bash",
                )
            else:
                args = command.split(" ")
                p = Popen(
                    args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    close_fds=MyEnv.platform_is_unix,
                    shell=False,
                    env=env,
                    universal_newlines=False,
                    cwd=cwd,
                    bufsize=0,
                )

            # set the O_NONBLOCK flag of p.stdout file descriptor:
            flags = fcntl(p.stdout, F_GETFL)  # get current p.stdout flags
            flags = fcntl(p.stderr, F_GETFL)  # get current p.stderr flags
            fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)
            fcntl(p.stderr, F_SETFL, flags | O_NONBLOCK)

            out = ""
            err = ""

            if async_:
                return p

            def readout(stream):
                if MyEnv.platform_is_unix:
                    # Store all intermediate data
                    data = list()
                    while True:
                        # Read out all available data
                        line = stream.read()
                        if not line:
                            break
                        line = line.decode()  # will be utf8
                        # Honour subprocess univeral_newlines
                        if p.universal_newlines:
                            line = p._translate_newlines(line)
                        # Add data to cache
                        data.append(line)
                        if showout:
                            Tools.pprint(line, end="")

                    # Fold cache and return
                    return "".join(data)

                else:
                    # This is not UNIX, most likely Win32. read() seems to work
                    def readout(stream):
                        line = stream.read().decode()
                        if showout:
                            # Tools.log(line)
                            Tools.pprint(line, end="")

            if timeout < 0:
                out, err = p.communicate()
                out = out.decode()
                err = err.decode()

            else:  # timeout set
                start = time.time()
                end = start + timeout
                now = start

                # if command already finished then read stdout, stderr
                out = readout(p.stdout)
                err = readout(p.stderr)
                if (out is None or err is None) and p.poll() is None:
                    raise RuntimeError("prob bug, needs to think this through, seen the while loop")
                while p.poll() is None:
                    # means process is still running

                    time.sleep(0.01)
                    now = time.time()
                    # print("wait")

                    if timeout != 0 and now > end:
                        if MyEnv.platform_is_unix:
                            # Soft and hard kill on Unix
                            try:
                                p.terminate()
                                # Give the process some time to settle
                                time.sleep(0.2)
                                p.kill()
                            except OSError:
                                pass
                        else:
                            # Kill on anything else
                            time.sleep(0.1)
                            if p.poll():
                                p.terminate()
                        if MyEnv.debug or log:
                            Tools.log("process killed because of timeout", level=30)
                        return (-2, out, err)

                    # Read out process streams, but don't block
                    out += readout(p.stdout)
                    err += readout(p.stderr)

            rc = -1 if p.returncode < 0 else p.returncode

            if rc < 0 or rc > 0:
                if MyEnv.debug or log:
                    Tools.log("system.process.run ended, exitcode was %d" % rc)
            # if out!="":
            #     Tools.log('system.process.run stdout:\n%s' % out)
            # if err!="":
            #     Tools.log('system.process.run stderr:\n%s' % err)

            if die and rc != 0:
                msg = "\nCould not execute:"
                if command.find("\n") == -1 and len(command) < 40:
                    msg += " '%s'" % command
                else:
                    command = "\n".join(command.split(";"))
                    msg += Tools.text_indent(command).rstrip() + "\n\n"
                if out.strip() != "":
                    msg += "stdout:\n"
                    msg += Tools.text_indent(out).rstrip() + "\n\n"
                if err.strip() != "":
                    msg += "stderr:\n"
                    msg += Tools.text_indent(err).rstrip() + "\n\n"
                raise RuntimeError(msg)

            # close the files (otherwise resources get lost),
            # wait for the process to die, and del the Popen object
            p.stdin.close()
            p.stderr.close()
            p.stdout.close()
            p.wait()
            del p

            return (rc, out, err)

    # @staticmethod
    # def run(script,die=True,args={},interactive=True,showout=True):
    #     if "\n" in script:
    #         script = Tools.text_strip(script,args=args)
    #         if showout:
    #             if "\n" in script:
    #                 Tools.log("RUN:\n%s"%script)
    #             else:
    #                 Tools.log("RUN: %s"%script)
    #         path_script = "/tmp/jumpscale/run_script.sh"
    #         p = Path(path_script)
    #         p.write_text(script)
    #         return Tools._execute("bash %s"%path_script,die=die,interactive=interactive,showout=showout)
    #     else:
    #         return Tools._execute(cmd=script, args=None, die=die, interactive=interactive, showout=showout)
    #

    @staticmethod
    def process_pids_get_by_filter(filterstr, excludes=[]):
        cmd = "ps ax | grep '%s'" % filterstr
        rcode, out, err = Tools.execute(cmd)
        # print out
        found = []

        def checkexclude(c, excludes):
            for item in excludes:
                c = c.lower()
                if c.find(item.lower()) != -1:
                    return True
            return False

        for line in out.split("\n"):
            if line.find("grep") != -1 or line.strip() == "":
                continue
            if line.strip() != "":
                if line.find(filterstr) != -1:
                    line = line.strip()
                    if not checkexclude(line, excludes):
                        # print "found pidline:%s"%line
                        found.append(int(line.split(" ")[0]))
        return found

    @staticmethod
    def process_kill_by_pid(pid):
        Tools.execute("kill -9 %s" % pid)

    @staticmethod
    def process_kill_by_by_filter(filterstr):
        for pid in Tools.process_pids_get_by_filter(filterstr):
            Tools.process_kill_by_pid(pid)

    @staticmethod
    def ask_choices(msg, choices=[], default=None):
        Tools._check_interactive()
        msg = Tools.text_strip(msg)
        print(msg)
        if "\n" in msg:
            print()
        choices = [str(i) for i in choices if i not in [None, "", ","]]
        choices_txt = ",".join(choices)
        mychoice = input("make your choice (%s): " % choices_txt)
        while mychoice not in choices:
            if mychoice.strip() == "" and default:
                return default
            print("ERROR: only choose %s please" % choices_txt)
            mychoice = input("make your choice (%s): " % choices_txt)
        return mychoice

    @staticmethod
    def ask_yes_no(msg, default="y"):
        """

        :param msg: the msg to show when asking for y or no
        :return: will return True if yes
        """
        Tools._check_interactive()
        return Tools.ask_choices(msg, "y,n", default=default) in ["y", ""]

    @staticmethod
    def _check_interactive():
        if not MyEnv.interactive:
            raise RuntimeError("Cannot use console in a non interactive mode.", "console.noninteractive")

    @staticmethod
    def ask_password(question="give secret", confirm=True, regex=None, retry=-1, validate=None):
        """Present a password input question to the user

        @param question: Password prompt message
        @param confirm: Ask to confirm the password
        @type confirm: bool
        @param regex: Regex to match in the response
        @param retry: Integer counter to retry ask for respone on the question
        @param validate: Function to validate provided value

        @returns: Password provided by the user
        @rtype: string
        """
        Tools._check_interactive()

        import getpass

        startquestion = question
        if question.endswith(": "):
            question = question[:-2]
        question += ": "
        value = None
        failed = True
        retryCount = retry
        while retryCount != 0:
            response = getpass.getpass(question)
            if (not regex or re.match(regex, response)) and (not validate or validate(response)):
                if value == response or not confirm:
                    return response
                elif not value:
                    failed = False
                    value = response
                    question = "%s (confirm): " % (startquestion)
                else:
                    value = None
                    failed = True
                    question = "%s: " % (startquestion)
            if failed:
                print("Invalid password!")
                retryCount = retryCount - 1
        raise RuntimeError(
            (
                "Console.askPassword() failed: tried %s times but user didn't fill out a value that matches '%s'."
                % (retry, regex)
            ),
            "console.ask_password",
        )

    @staticmethod
    def ask_string(msg, default=None):
        Tools._check_interactive()
        msg = Tools.text_strip(msg)
        print(msg)
        if "\n" in msg:
            print()
        txt = input()
        if default and txt.strip() == "":
            txt = default
        return txt

    @staticmethod
    def cmd_installed(name):
        if not name in MyEnv._cmd_installed:
            MyEnv._cmd_installed[name] = shutil.which(name) != None
        return MyEnv._cmd_installed[name]

    @staticmethod
    def cmd_args_get():
        res = {}
        for i in sys.argv[1:]:
            if "=" in i:
                name, val = i.split("=", 1)
                name = name.strip("-").strip().strip("-")
                val = val.strip().strip("'").strip('"').strip()
                res[name.lower()] = val
            elif i.strip() != "":
                name = i.strip("-").strip().strip("-")
                res[name.lower()] = True
        return res

    @staticmethod
    def tcp_port_connection_test(ipaddr, port, timeout=None):
        conn = None
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if timeout:
                conn.settimeout(timeout)
            try:
                conn.connect((ipaddr, port))
            except BaseException:
                return False
        finally:
            if conn:
                conn.close()
        return True

    @staticmethod
    def _code_location_get(account, repo):
        """
        accountdir will be created if it does not exist yet
        :param repo:
        :param static: static means we don't use git

        :return: repodir_exists,foundgit, accountdir,repodir

            foundgit means, we found .git in the repodir
            dontpull means, we found .dontpull in the repodir, means code is being synced to the repo from remote, should not update

        """
        prefix = "code"
        if "DIR_CODE" in MyEnv.config:
            accountdir = os.path.join(MyEnv.config["DIR_CODE"], "github", account)
        else:
            accountdir = os.path.join(MyEnv.config["DIR_BASE"], prefix, "github", account)
        repodir = os.path.join(accountdir, repo)
        gitdir = os.path.join(repodir, ".git")
        dontpullloc = os.path.join(repodir, ".dontpull")
        if os.path.exists(accountdir):
            if os.listdir(accountdir) == []:
                shutil.rmtree(accountdir)  # lets remove the dir & return it does not exist

        exists = os.path.exists(repodir)
        foundgit = os.path.exists(gitdir)
        dontpull = os.path.exists(dontpullloc)
        return exists, foundgit, dontpull, accountdir, repodir

    @staticmethod
    def code_changed(path):
        """
        check if there is code in there which changed
        :param path:
        :return:
        """
        S = """
        cd {REPO_DIR}
        git diff --exit-code || exit 1
        git diff --cached --exit-code || exit 1
        if git status --porcelain | grep .; then
            exit 1
        else
            exit 0
        fi
        """
        args = {}
        args["REPO_DIR"] = path
        rc, out, err = Tools.execute(S, showout=False, die=False, args=args)
        return rc > 0

    @staticmethod
    def code_github_get(repo, account="threefoldtech", branch=None, pull=True, reset=False):
        """

        :param repo:
        :param account:
        :param branch: is list of branches
        :param pull:
        :param reset:
        :return:
        """
        Tools.log("get code:%s:%s (%s)" % (repo, account, branch))
        if MyEnv.config["SSH_AGENT"]:
            url = "git@github.com:%s/%s.git"
        else:
            url = "https://github.com/%s/%s.git"

        repo_url = url % (account, repo)
        exists, foundgit, dontpull, ACCOUNT_DIR, REPO_DIR = Tools._code_location_get(account=account, repo=repo)

        if reset:
            Tools.delete(REPO_DIR)
            exists, foundgit, dontpull, ACCOUNT_DIR, REPO_DIR = Tools._code_location_get(account=account, repo=repo)

        args = {}
        args["ACCOUNT_DIR"] = ACCOUNT_DIR
        args["REPO_DIR"] = REPO_DIR
        args["URL"] = repo_url
        args["NAME"] = repo

        if branch is None:
            branch = ["development", "master"]
        elif isinstance(branch, str):
            if "," in branch:
                branch = [branch.strip() for branch in branch.split(",")]
        elif isinstance(branch, (set, list)):
            branch = [branch.strip() for branch in branch]
        else:
            raise RuntimeError("branch should be a string or list, now %s" % branch)

        args["BRANCH"] = branch[0]

        if "GITPULL" in os.environ:
            pull = str(os.environ["GITPULL"]) == "1"

        git_on_system = Tools.cmd_installed("git")

        if git_on_system and MyEnv.config["USEGIT"] and ((exists and foundgit) or not exists):
            # there is ssh-key loaded
            # or there is a dir with .git inside and exists
            # or it does not exist yet
            # then we need to use git

            C = ""

            if exists is False:
                C = """
                set -e
                mkdir -p {ACCOUNT_DIR}
                """
                Tools.log("get code [git] (first time): %s" % repo)
                Tools.execute(C, args=args, showout=False)
                C = """
                cd {ACCOUNT_DIR}
                git clone  --depth 1 {URL} -b {BRANCH}
                cd {NAME}
                """
                rc, _, _ = Tools.execute(C, args=args, die=False, showout=False)
                if rc > 0:
                    C = """
                    cd {ACCOUNT_DIR}
                    git clone {URL}
                    cd {NAME}
                    """
                    rc, _, _ = Tools.execute(C, args=args, die=True, showout=False)

            else:
                if pull:
                    if reset:
                        C = """
                        set -x
                        cd {REPO_DIR}
                        git checkout . --force
                        git pull
                        """
                        Tools.log("get code & ignore changes: %s" % repo)
                        Tools.execute(C, args=args)
                    elif Tools.code_changed(REPO_DIR):
                        if Tools.ask_yes_no("\n**: found changes in repo '%s', do you want to commit?" % repo):
                            if "GITMESSAGE" in os.environ:
                                args["MESSAGE"] = os.environ["GITMESSAGE"]
                            else:
                                args["MESSAGE"] = input("\nprovide commit message: ")
                                assert args["MESSAGE"].strip() != ""
                        else:
                            print("found changes, do not want to commit")
                            sys.exit(1)
                        C = """
                        set -x
                        cd {REPO_DIR}
                        git add . -A
                        git commit -m "{MESSAGE}"
                        git pull

                        """
                        Tools.log("get code & commit [git]: %s" % repo)
                        Tools.execute(C, args=args)

            def getbranch(args):
                cmd = "cd {REPO_DIR}; git branch | grep \* | cut -d ' ' -f2"
                rc, stdout, err = Tools.execute(cmd, die=False, args=args, interactive=False)
                if rc > 0:
                    Tools.shell()
                current_branch = stdout.strip()
                Tools.log("Found branch: %s" % current_branch)
                return current_branch

            def checkoutbranch(args, branch):
                args["BRANCH"] = branch
                current_branch = getbranch(args=args)
                if current_branch != branch:
                    script = """
                    set -ex
                    cd {REPO_DIR}
                    git checkout {BRANCH} -f
                    """
                    rc, out, err = Tools.execute(script, die=False, args=args, showout=True, interactive=False)
                    if rc > 0:
                        return False
                    assert getbranch(args=args) == branch
                return True

            for branch_item in branch:
                if checkoutbranch(args, branch_item):
                    return

            raise RuntimeError("Could not checkout branch:%s on %s" % (branch, args["REPO_DIR"]))

        else:
            Tools.log("get code [zip]: %s" % repo)
            download = False
            if download == False and (not exists or (not dontpull and pull)):

                for branch_item in branch:
                    branch_item = branch_item.strip()
                    url_http = "https://github.com/%s/%s/archive/%s.zip" % (account, repo, branch_item)

                    args = {}
                    args["ACCOUNT_DIR"] = ACCOUNT_DIR
                    args["REPO_DIR"] = REPO_DIR
                    args["URL"] = url_http
                    args["NAME"] = repo
                    args["BRANCH"] = branch_item

                    script = """
                    set -ex
                    cd {DIR_TEMP}
                    rm -f download.zip
                    curl -L {URL} > download.zip
                    """
                    Tools.execute(script, args=args, die=False)
                    statinfo = os.stat("/tmp/jumpscale/download.zip")
                    if statinfo.st_size < 100000:
                        continue
                    else:
                        script = """
                        set -ex
                        cd {DIR_TEMP}
                        rm -rf {NAME}-{BRANCH}
                        mkdir -p {REPO_DIR}
                        rm -rf {REPO_DIR}
                        unzip download.zip > /tmp/unzip
                        mv {NAME}-{BRANCH} {REPO_DIR}
                        rm -f download.zip
                        """
                        try:
                            Tools.execute(script, args=args, die=True)
                        except Exception as e:
                            Tools.shell()
                        download = True

            if not exists and download == False:
                raise RuntimeError("Could not download some code")

    @staticmethod
    def config_load(path="", if_not_exist_create=False, executor=None, content=""):
        """
        only 1 level deep toml format only for int,string,bool
        no multiline support for text fields

        return dict

        """
        res = {}
        if content == "":
            if executor is None:
                if os.path.exists(path):
                    t = Tools.file_text_read(path)
                else:
                    if if_not_exist_create:
                        Tools.config_save(path, {})
                    return {}
            else:
                if executor.exists(path):
                    t = executor.file_read(path)
                else:
                    if if_not_exist_create:
                        Tools.config_save(path, {}, executor=executor)
                    return {}
        else:
            t = content

        for line in t.split("\n"):
            if line.strip() == "":
                continue
            if line.startswith("#"):
                continue
            key, val = line.split("=", 1)
            if "#" in val:
                val = val.split("#", 1)[0]
            key = key.strip().upper()
            val = val.strip().strip("'").strip().strip('"').strip()
            if str(val).lower() in [0, "false", "n", "no"]:
                val = False
            elif str(val).lower() in [1, "true", "y", "yes"]:
                val = True
            elif str(val).find("[") != -1:
                val2 = str(val).strip("[").strip("]")
                val = [
                    item.strip().strip("'").strip().strip('"').strip() for item in val2.split(",") if item.strip() != ""
                ]
            else:
                try:
                    val = int(val)
                except:
                    pass
            res[key] = val

        return res

    @staticmethod
    def config_save(path, data, executor=None):
        out = ""
        for key, val in data.items():
            key = key.upper()
            if isinstance(val, list):
                val2 = "["
                for item in val:
                    val2 += "'%s'," % item
                val2 = val2.rstrip(",")
                val2 += "]"
                val = val2
            elif isinstance(val, str):
                val = "'%s'" % val

            if val == True:
                val = "true"
            if val == False:
                val = "false"
            out += "%s = %s\n" % (key, val)

        if executor:
            executor.file_write(path, out)
        else:
            Tools.file_write(path, out)


LOGFORMATBASE = (
    "{COLOR}{TIME} {filename:<16}{RESET} -{linenr:4d} - {GRAY}{context:<35}{RESET}: {message}"
)  # DO NOT CHANGE COLOR


class MyEnv:

    readonly = False  # if readonly will not manipulate local filesystem appart from /tmp
    sandbox_python_active = False  # means we have a sandboxed environment where python3 works in
    sandbox_lua_active = False  # same for lua
    config_changed = False
    _cmd_installed = {}
    state = None
    __init = False
    debug = False

    sshagent = None
    interactive = False

    appname = "installer"

    FORMAT_TIME = "%a %d %H:%M:%S"

    MYCOLORS = {
        "RED": "\033[1;31m",
        "BLUE": "\033[1;34m",
        "CYAN": "\033[1;36m",
        "GREEN": "\033[0;32m",
        "GRAY": "\033[0;37m",
        "YELLOW": "\033[0;33m",
        "RESET": "\033[0;0m",
        "BOLD": "\033[;1m",
        "REVERSE": "\033[;7m",
    }

    LOGFORMAT = {
        "DEBUG": LOGFORMATBASE.replace("{COLOR}", "{CYAN}"),
        "STDOUT": "{message}",
        # 'INFO': '{BLUE}* {message}{RESET}',
        "INFO": LOGFORMATBASE.replace("{COLOR}", "{BLUE}"),
        "WARNING": LOGFORMATBASE.replace("{COLOR}", "{YELLOW}"),
        "ERROR": LOGFORMATBASE.replace("{COLOR}", "{RED}"),
        "CRITICAL": "{RED}{TIME} {filename:<16} -{linenr:4d} - {GRAY}{context:<35}{RESET}: {message}",
    }

    db = RedisTools.client_core_get(die=False)

    @staticmethod
    def platform():
        """
        will return one of following strings:
            linux, darwin

        """
        return sys.platform

    # @staticmethod
    # def platform_is_linux():
    #     return "posix" in sys.builtin_module_names

    @staticmethod
    def check_platform():
        """check if current platform is supported (linux or darwin)
        for linux, the version check is done by `UbuntuInstaller.ensure_version()`

        :raises RuntimeError: in case platform is not supported
        """
        platform = MyEnv.platform()
        if "linux" in platform:
            UbuntuInstaller.ensure_version()
        elif "darwin" not in platform:
            raise RuntimeError("Your platform is not supported")

    @staticmethod
    def _homedir_get():
        if "HOMEDIR" in os.environ:
            dir_home = os.environ["HOMEDIR"]
        elif "HOME" in os.environ:
            dir_home = os.environ["HOME"]
        else:
            dir_home = "/root"
        return dir_home

    @staticmethod
    def _basedir_get():
        if MyEnv.readonly:
            return "/tmp/jumpscale"
        if Tools.exists("/sandbox"):
            return "/sandbox"
        p = "%s/sandbox" % MyEnv._homedir_get()
        if not Tools.exists(p):
            Tools.dir_ensure(p)
        return p

    @staticmethod
    def _cfgdir_get():
        if MyEnv.readonly:
            return "/tmp/jumpscale/cfg"
        return "%s/cfg" % MyEnv._basedir_get()

    @staticmethod
    def config_default_get(config={}):

        if "DIR_BASE" not in config:
            config["DIR_BASE"] = MyEnv._basedir_get()

        if "DIR_HOME" not in config:
            config["DIR_HOME"] = MyEnv._homedir_get()

        if not "DIR_CFG" in config:
            config["DIR_CFG"] = MyEnv._cfgdir_get()

        if not "USEGIT" in config:
            config["USEGIT"] = True
        if not "READONLY" in config:
            config["READONLY"] = False
        if not "DEBUG" in config:
            config["DEBUG"] = False
        if not "INTERACTIVE" in config:
            config["INTERACTIVE"] = True
        if not "SECRET" in config:
            config["SECRET"] = ""

        config["SSH_AGENT"] = True
        config["SSH_KEY_DEFAULT"] = ""

        config["LOGGER_INCLUDE"] = ["*"]
        config["LOGGER_EXCLUDE"] = ["sal.fs"]
        config["LOGGER_LEVEL"] = 15  # means std out & plus gets logged
        config["LOGGER_CONSOLE"] = True
        config["LOGGER_REDIS"] = False

        if MyEnv.readonly:
            config["DIR_TEMP"] = "/tmp/jumpscale_installer"
            config["LOGGER_REDIS"] = False
            config["LOGGER_CONSOLE"] = True

        if not "DIR_TEMP" in config:
            config["DIR_TEMP"] = "/tmp/jumpscale"
        if not "DIR_VAR" in config:
            config["DIR_VAR"] = "%s/var" % config["DIR_BASE"]
        if not "DIR_CODE" in config:
            config["DIR_CODE"] = "%s/code" % config["DIR_BASE"]
            # if Tools.exists("%s/code" % config["DIR_BASE"]):
            #     config["DIR_CODE"] = "%s/code" % config["DIR_BASE"]
            # else:
            #     config["DIR_CODE"] = "%s/code" % config["DIR_HOME"]
        if not "DIR_BIN" in config:
            config["DIR_BIN"] = "%s/bin" % config["DIR_BASE"]
        if not "DIR_APPS" in config:
            config["DIR_APPS"] = "%s/apps" % config["DIR_BASE"]

        return config

    @staticmethod
    def _init():
        if not MyEnv.__init:
            raise RuntimeError("myenv should have been inited by system")

    # def configure_help():
    #     C = """
    #     Configuration for JSX initialisation:
    #
    #     --basedir=                      default ~/sandbox or /sandbox whatever exists first
    #     --configdir=                    default $BASEDIR/cfg
    #     --codedir=                     default $BASEDIR/code
    #
    #     --sshkey=                       key to use for ssh-agent if any
    #     --sshagent-no                   default is to use the sshagent, if you want to disable use this flag
    #
    #     --readonly                      default is false
    #     --no_interactive                default is interactive, means will ask questions
    #     --debug_configure               default debug_configure is False, will configure in debug mode
    #     """
    #     return Tools.text_strip(C)

    @staticmethod
    def configure(
        configdir=None,
        basedir=None,
        codedir=None,
        config={},
        readonly=None,
        sshkey=None,
        sshagent_use=None,
        debug_configure=None,
        secret=None,
        interactive=True,
    ):
        """

        the args of the command line will also be parsed, will check for

        --basedir=                      default ~/sandbox or /sandbox whatever exists first
        --configdir=                    default $BASEDIR/cfg
        --codedir=                     default $BASEDIR/code

        --sshkey=                       key to use for ssh-agent if any
        --no_sshagent                  default is to use the sshagent, if you want to disable use this flag

        --readonly                      default is false
        --no_interactive                default is interactive, means will ask questions
        --debug_configure               default debug_configure is False, will configure in debug mode

        :param configdir: is the directory where all configuration & keys will be stored
        :param basedir: the root of the sandbox
        :param config: configuration arguments which go in the config file
        :param readonly: specific mode of operation where minimal changes will be done while using JSX
        :param codedir: std $sandboxdir/code
        :param sshkey: name of the sshkey to use if there are more than 1 in ssh-agent
        :param sshagent_use: needs to be True if sshkey used
        :return:
        """

        if not os.path.exists(MyEnv.config_file_path):
            MyEnv.config = MyEnv.config_default_get(config=config)
        else:
            MyEnv._config_load()

        if interactive not in [True, False]:
            raise RuntimeError("interactive is True or False")
        MyEnv.interactive = interactive
        args = Tools.cmd_args_get()

        if configdir is None and "configdir" in args:
            configdir = args["configdir"]
        if codedir is None and "codedir" in args:
            codedir = args["codedir"]
        if basedir is None and "basedir" in args:
            basedir = args["basedir"]
        if sshkey is None and "sshkey" in args:
            sshkey = args["sshkey"]

        if readonly is None and "readonly" in args:
            readonly = True

        if interactive and "no_interactive" in args:
            interactive = False
        if sshagent_use is None or ("no_sshagent" in args and sshagent_use is False):
            sshagent_use = False
        else:
            sshagent_use = True
        if debug_configure is None and "debug_configure" in args:
            debug_configure = True

        if not configdir:
            if "DIR_CFG" in config:
                configdir = config["DIR_CFG"]
            elif "JSX_DIR_CFG" in os.environ:
                configdir = os.environ["JSX_DIR_CFG"]
            else:
                configdir = MyEnv._cfgdir_get()
        config["DIR_CFG"] = configdir

        # installpath = os.path.dirname(inspect.getfile(os.path))
        # # MEI means we are pyexe BaseInstaller
        # if installpath.find("/_MEI") != -1 or installpath.endswith("dist/install"):
        #     pass  # dont need yet but keep here

        if not basedir:
            if "DIR_BASE" in config:
                basedir = config["DIR_BASE"]
            else:
                basedir = MyEnv._basedir_get()

        config["DIR_BASE"] = basedir

        if basedir == "/sandbox" and not os.path.exists(basedir):
            script = """
            set -ex
            cd /
            sudo mkdir -p {DIR_BASE}/cfg
            sudo chown -R {USERNAME}:{GROUPNAME} {DIR_BASE}
            mkdir -p /usr/local/EGG-INFO
            sudo chown -R {USERNAME}:{GROUPNAME} /usr/local/EGG-INFO
            """
            args = {}
            args["DIR_BASE"] = basedir
            args["USERNAME"] = getpass.getuser()
            st = os.stat(MyEnv.config["DIR_HOME"])
            gid = st.st_gid
            args["GROUPNAME"] = grp.getgrgid(gid)[0]
            Tools.execute(script, interactive=True, args=args)

        MyEnv.config_file_path = os.path.join(config["DIR_CFG"], "jumpscale_config.toml")
        MyEnv.state_file_path = os.path.join(config["DIR_CFG"], "jumpscale_done.toml")

        if codedir is not None:
            config["DIR_CODE"] = codedir

        if not "DIR_TEMP" in MyEnv.config:
            config.update(MyEnv.config)
            MyEnv.config = MyEnv.config_default_get(config=config)

        if readonly:
            MyEnv.config["READONLY"] = readonly
        if interactive:
            MyEnv.config["INTERACTIVE"] = interactive
        if sshagent_use:
            MyEnv.config["SSH_AGENT"] = sshagent_use
        if sshkey:
            MyEnv.config["SSH_KEY_DEFAULT"] = sshkey
        if debug_configure:
            MyEnv.config["DEBUG"] = debug_configure

        for key, val in config.items():
            MyEnv.config[key] = val

        if not sshagent_use and interactive:  # just a warning when interactive
            T = """
            Is it ok to continue without SSH-Agent, are you sure?
            It's recommended to have a SSH key as used on github loaded in your ssh-agent
            If the SSH key is not found, repositories will be cloned using https

            if you never used an ssh-agent or github, just say "y"

            """
            print(Tools.text_strip(T))
            if interactive:
                if not Tools.ask_yes_no("OK to continue?"):
                    sys.exit(1)

        # defaults are now set, lets now configure the system
        if False and sshagent_use:
            # TODO: this is an error SSH_agent does not work because cannot identify which private key to use
            # see also: https://github.com/threefoldtech/jumpscaleX/issues/561
            MyEnv.sshagent = SSHAgent()
            MyEnv.sshagent.key_default
        else:
            if secret is None:
                if "SECRET" not in MyEnv.config or not MyEnv.config["SECRET"]:
                    if interactive:
                        while not secret:  # keep asking till the secret is not empty
                            secret = Tools.ask_password("provide secret to use for encrypting private key")
                    else:
                        print("NEED TO SPECIFY SECRET WHEN SSHAGENT NOT USED")
                        sys.exit(1)
                else:
                    secret = MyEnv.config["SECRET"]
            if secret:
                MyEnv.secret_set(secret)
                # is same as what is used to read from ssh-agent in SSHAgent client
            else:
                print("SECRET IS NEEDED")
                sys.exit(1)  # we must have a secret here otherwise it will fails later on

        MyEnv.config_save()
        MyEnv.init(configdir=configdir)

    @staticmethod
    def secret_set(secret=None):
        while not secret:  # keep asking till the secret is not empty
            secret = Tools.ask_password("provide secret to use for encrypting private key")
        secret = secret.encode()

        import hashlib

        m = hashlib.sha256()
        m.update(secret)

        secret2 = m.hexdigest()

        if MyEnv.config["SECRET"] != secret2:

            MyEnv.config["SECRET"] = secret2

            MyEnv.config_save()

    @staticmethod
    def init(configdir=None, reset=False):
        """

        :param configdir: default /sandbox/cfg, then ~/sandbox/cfg if not exists
        :return:
        """
        if reset is False and MyEnv.__init:
            return

        print("MYENV INIT")

        args = Tools.cmd_args_get()

        if MyEnv.platform() == "linux":
            MyEnv.platform_is_linux = True
            MyEnv.platform_is_unix = True
            MyEnv.platform_is_osx = False
        elif "darwin" in MyEnv.platform():
            MyEnv.platform_is_linux = False
            MyEnv.platform_is_unix = True
            MyEnv.platform_is_osx = True
        else:
            raise RuntimeError("platform not supported, only linux or osx for now.")

        if not configdir:
            if "JSX_DIR_CFG" in os.environ:
                configdir = os.environ["JSX_DIR_CFG"]
            else:
                if configdir is None and "configdir" in args:
                    configdir = args["configdir"]
                else:
                    configdir = MyEnv._cfgdir_get()

        MyEnv.config_file_path = os.path.join(configdir, "jumpscale_config.toml")
        MyEnv.state_file_path = os.path.join(configdir, "jumpscale_done.toml")

        if Tools.exists(MyEnv.config_file_path):
            MyEnv._config_load()
            if not "DIR_BASE" in MyEnv.config:
                return

            MyEnv.log_includes = [i for i in MyEnv.config.get("LOGGER_INCLUDE", []) if i.strip().strip("''") != ""]
            MyEnv.log_excludes = [i for i in MyEnv.config.get("LOGGER_EXCLUDE", []) if i.strip().strip("''") != ""]
            MyEnv.log_loglevel = MyEnv.config.get("LOGGER_LEVEL", 100)
            MyEnv.log_console = MyEnv.config.get("LOGGER_CONSOLE", True)
            MyEnv.log_redis = MyEnv.config.get("LOGGER_REDIS", False)
            MyEnv.debug = MyEnv.config.get("DEBUG", False)
            MyEnv.interactive = MyEnv.config.get("INTERACTIVE", True)

            if os.path.exists(os.path.join(MyEnv.config["DIR_BASE"], "bin", "python3.6")):
                MyEnv.sandbox_python_active = True
            else:
                MyEnv.sandbox_python_active = False

            MyEnv._state_load()

            if MyEnv.config["SSH_AGENT"]:
                MyEnv.sshagent = SSHAgent()

            MyEnv.__init = True

    @staticmethod
    def config_edit():
        """
        edits the configuration file which is in {DIR_BASE}/cfg/jumpscale_config.toml
        {DIR_BASE} normally is /sandbox
        """
        Tools.file_edit(MyEnv.config_file_path)

    @staticmethod
    def _config_load():
        """
        loads the configuration file which default is in {DIR_BASE}/cfg/jumpscale_config.toml
        {DIR_BASE} normally is /sandbox
        """
        MyEnv.config = Tools.config_load(MyEnv.config_file_path)

    @staticmethod
    def config_save():
        Tools.config_save(MyEnv.config_file_path, MyEnv.config)

    @staticmethod
    def _state_load():
        """
        only 1 level deep toml format only for int,string,bool
        no multiline
        """
        if Tools.exists(MyEnv.state_file_path):
            MyEnv.state = Tools.config_load(MyEnv.state_file_path, if_not_exist_create=False)
        elif not MyEnv.readonly:
            MyEnv.state = Tools.config_load(MyEnv.state_file_path, if_not_exist_create=True)
        else:
            MyEnv.state = {}

    @staticmethod
    def state_save():
        if MyEnv.readonly:
            return
        Tools.config_save(MyEnv.state_file_path, MyEnv.state)

    @staticmethod
    def _key_get(key):
        key = key.split("=", 1)[0]
        key = key.split(">", 1)[0]
        key = key.split("<", 1)[0]
        key = key.split(" ", 1)[0]
        key = key.upper()
        return key

    @staticmethod
    def state_get(key):
        key = MyEnv._key_get(key)
        if key in MyEnv.state:
            return True
        return False

    @staticmethod
    def state_set(key):
        if MyEnv.readonly:
            return
        key = MyEnv._key_get(key)
        MyEnv.state[key] = True
        MyEnv.state_save()

    @staticmethod
    def state_delete(key):
        if MyEnv.readonly:
            return
        key = MyEnv._key_get(key)
        if key in MyEnv.state:
            MyEnv.state.pop(key)
            MyEnv.state_save()

    @staticmethod
    def state_reset():
        """
        remove all state
        """
        Tools.delete(MyEnv.state_file_path)
        MyEnv._state_load()


class BaseInstaller:
    @staticmethod
    def install(configdir=None, force=False, sandboxed=False):

        MyEnv.init(configdir=configdir)

        if force:
            MyEnv.state_delete("install")

        if MyEnv.state_get("install"):
            return  # nothing to do

        BaseInstaller.base()
        if MyEnv.platform() == "linux":
            if not sandboxed:
                UbuntuInstaller.do_all()
            else:
                raise RuntimeError("not ok yet")
                UbuntuInstaller.base()
        elif "darwin" in MyEnv.platform():
            if not sandboxed:
                OSXInstaller.do_all()
            else:
                raise RuntimeError("not ok yet")
                OSXInstaller.base()
        else:
            raise RuntimeError("only OSX and Linux Ubuntu supported.")

        # BASHPROFILE
        if sandboxed:
            env_path = "%s/.bash_profile" % MyEnv.config["DIR_HOME"]
            if Tools.exists(env_path):
                bashprofile = Tools.file_text_read(env_path)
                cmd = "source /sandbox/env.sh"
                if bashprofile.find(cmd) != -1:
                    bashprofile = bashprofile.replace(cmd, "")
                    Tools.file_write(env_path, bashprofile)
        else:
            # if not sandboxed need to remove old python's from bin dir
            Tools.execute("rm -f {DIR_BASE}/bin/pyth*")
            env_path = "%s/.bash_profile" % MyEnv.config["DIR_HOME"]
            if not Tools.exists(env_path):
                bashprofile = ""
            else:
                bashprofile = Tools.file_text_read(env_path)
            cmd = "source /sandbox/env.sh"
            if bashprofile.find(cmd) == -1:
                bashprofile += "\n%s\n" % cmd
                Tools.file_write(env_path, bashprofile)

        print("- get sandbox base from git")
        Tools.code_github_get(repo="sandbox_base", branch=["master"], pull=False)
        print("- copy files to sandbox")
        # will get the sandbox installed
        if not sandboxed:

            script = """
            set -e
            cd {DIR_BASE}
            rsync -rav {DIR_BASE}/code/github/threefoldtech/sandbox_base/base/cfg/ {DIR_BASE}/cfg/
            rsync -rav {DIR_BASE}/code/github/threefoldtech/sandbox_base/base/bin/ {DIR_BASE}/bin/
            rsync -rav {DIR_BASE}/code/github/threefoldtech/sandbox_base/base/openresty/ {DIR_BASE}/openresty/
            rsync -rav {DIR_BASE}/code/github/threefoldtech/sandbox_base/base/env.sh {DIR_BASE}/env.sh
            mkdir -p root
            mkdir -p var

            """
            Tools.execute(script, interactive=True)

        else:

            # install the sandbox

            raise RuntimeError("not done yet")

            script = """
            cd {DIR_BASE}
            rsync -ra {DIR_BASE}/code/github/threefoldtech/sandbox_base/base/ {DIR_BASE}/
            mkdir -p root
            """
            Tools.execute(script, interactive=True)

            if MyEnv.platform() == "darwin":
                reponame = "sandbox_osx"
            elif MyEnv.platform() == "linux":
                reponame = "sandbox_ubuntu"
            else:
                raise RuntimeError("cannot install, MyEnv.platform() now found")

            Tools.code_github_get(repo=reponame, branch=["master"])

            script = """
            set -ex
            cd {DIR_BASE}
            rsync -ra code/github/threefoldtech/{REPONAME}/base/ .
            mkdir -p root
            mkdir -p var
            """
            args = {}
            args["REPONAME"] = reponame

            Tools.execute(script, interactive=True, args=args)

            script = """
            set -e
            cd {DIR_BASE}
            source env.sh
            python3 -c 'print("- PYTHON OK, SANDBOX USABLE")'
            """
            Tools.execute(script, interactive=True)

            Tools.log("INSTALL FOR BASE OK")

        MyEnv.state_set("install")

    @staticmethod
    def base():

        if MyEnv.state_get("generic_base"):
            return

        if not os.path.exists(MyEnv.config["DIR_TEMP"]):
            os.makedirs(MyEnv.config["DIR_TEMP"], exist_ok=True)

        script = """

        mkdir -p {DIR_TEMP}/scripts
        mkdir -p {DIR_VAR}/log

        """
        Tools.execute(script, interactive=True)

        if MyEnv.platform_is_osx:
            OSXInstaller.base()
        elif MyEnv.platform_is_linux:
            UbuntuInstaller.base()
        else:
            print("Only ubuntu & osx supported")
            os.exit(1)

        MyEnv.state_set("generic_base")

    @staticmethod
    def pips_list(level=3):
        """
        level0 is only the most basic
        1 in the middle (recommended)
        2 is all pips
        """
        pips = {
            # level 0: most basic needed
            0: [
                "blosc>=1.5.1",
                "Brotli>=0.6.0",
                "captcha",
                "certifi",
                "Cython",
                "click>=6.6",
                "pygments-github-lexers",
                "colored-traceback>=0.2.2",
                "colorlog>=2.10.0",
                # "credis",
                "numpy",
                "cryptocompare",
                "cryptography>=2.2.0",
                "dnslib",
                "ed25519>=1.4",
                "fakeredis",
                "future>=0.15.0",
                "geopy",
                "geocoder",
                "gevent >= 1.2.2",
                "gipc",
                "GitPython>=2.1.1",
                "grequests>=0.3.0",
                "httplib2>=0.9.2",
                "ipcalc>=1.99.0",
                "ipython==6.5",
                "Jinja2>=2.9.6",
                "libtmux>=0.7.1",
                "msgpack-python>=0.4.8",
                "netaddr>=0.7.19",
                "netifaces>=0.10.6",
                "netstr",
                "npyscreen",
                "parallel_ssh>=1.4.0",
                "ssh2-python",
                "paramiko>=2.2.3",
                "path.py>=10.3.1",
                # "peewee>=2.9.2",
                "psutil>=5.4.3",
                "pudb>=2017.1.2",
                "pyblake2>=0.9.3",
                "pycapnp>=0.5.12",
                "PyGithub>=1.34",
                "pymux>=0.13",
                "pynacl>=1.2.1",
                "pyOpenSSL>=17.0.0",
                "pyserial>=3.0",
                "python-dateutil>=2.5.3",
                "pytoml>=0.1.2",
                "pyyaml",
                "redis>=2.10.5",
                "requests>=2.13.0",
                "six>=1.10.0",
                "sendgrid",
                "toml>=0.9.2",
                "Unidecode>=0.04.19",
                "watchdog>=0.8.3",
                "bpython",
                "pbkdf2",
                "ptpython",
                "pygments-markdown-lexer",
            ],
            # level 1: in the middle
            1: [
                "zerotier>=1.1.2",
                "python-jose>=2.0.1",
                "itsdangerous>=0.24",
                "jsonschema>=2.5.1",
                "graphene>=2.0",
                "gevent-websocket",
                "ovh>=0.4.7",
                "packet-python>=1.37",
                "uvloop>=0.8.0",
                "pycountry",
                "pycountry_convert",
                "cson>=0.7",
                "ujson",
                "Pillow>=4.1.1",
            ],
            # level 2: full install
            2: [
                # "psycopg2-binary",
                # "psycopg2>=2.7.1",
                "pystache>=0.5.4",
                # "pypandoc>=1.3.3",
                # "SQLAlchemy>=1.1.9",
                "pymongo>=3.4.0",
                "docker>=3",
                "dnspython>=1.15.0",
                "etcd3>=0.7.0",
                "Flask-Inputs>=0.2.0",
                "Flask>=0.12.2",
                "html2text",
                "influxdb>=4.1.0",
            ],
        }

        res = []

        for piplevel in pips:
            if piplevel <= level:
                res += pips[piplevel]

        return res

    @staticmethod
    def pips_install(items=None):
        if not items:
            items = BaseInstaller.pips_list(3)
        for pip in items:
            if not MyEnv.state_get("pip_%s" % pip):
                C = "pip3 install '%s'" % pip  # --user
                Tools.execute(C, die=True)
                MyEnv.state_set("pip_%s" % pip)


class OSXInstaller:
    @staticmethod
    def do_all():
        MyEnv._init()
        Tools.log("installing OSX version")
        OSXInstaller.base()
        BaseInstaller.pips_install()

    @staticmethod
    def base():
        MyEnv._init()
        OSXInstaller.brew_install()
        if not Tools.cmd_installed("curl") or not Tools.cmd_installed("unzip") or not Tools.cmd_installed("rsync"):
            script = """
            brew install curl unzip rsync
            """
            Tools.execute(script, replace=True)
        BaseInstaller.pips_install(["click"])  # TODO: *1

    @staticmethod
    def brew_install():
        if not Tools.cmd_installed("brew"):
            cmd = 'ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'
            Tools.execute(cmd, interactive=True)

    @staticmethod
    def brew_uninstall():
        MyEnv._init()
        cmd = 'ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall)"'
        Tools.execute(cmd, interactive=True)
        toremove = """
        sudo rm -rf /usr/local/.com.apple.installer.keep
        sudo rm -rf /usr/local/include/
        sudo rm -rf /usr/local/etc/
        sudo rm -rf /usr/local/var/
        sudo rm -rf /usr/local/FlashcardService/
        sudo rm -rf /usr/local/texlive/
        """
        Tools.execute(toremove, interactive=True)


class UbuntuInstaller:
    @staticmethod
    def do_all():
        MyEnv._init()
        Tools.log("installing Ubuntu version")

        UbuntuInstaller.ensure_version()
        UbuntuInstaller.base()
        # UbuntuInstaller.ubuntu_base_install()
        UbuntuInstaller.python_redis_install()
        UbuntuInstaller.apts_install()
        BaseInstaller.pips_install()

    @staticmethod
    def ensure_version():
        MyEnv._init()
        if not os.path.exists("/etc/lsb-release"):
            raise RuntimeError("Your operating system is not supported")

        return True

    @staticmethod
    def base():
        MyEnv._init()
        if MyEnv.state_get("base"):
            return

        rc, out, err = Tools.execute("lsb_release -a")
        if out.find("Ubuntu 18.04") != -1:
            bionic = True
        else:
            bionic = False

        if bionic:
            script = """
            if ! grep -Fq "deb http://mirror.unix-solutions.be/ubuntu/ bionic" /etc/apt/sources.list; then
                echo >> /etc/apt/sources.list
                echo "# Jumpscale Setup" >> /etc/apt/sources.list
                echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
            fi
            """
            Tools.execute(script, interactive=True)

        script = """
        apt-get update
        apt-get install -y curl rsync unzip
        locale-gen --purge en_US.UTF-8

        apt-get install python3-pip -y
        apt-get install locales -y

        """
        Tools.execute(script, interactive=True)

        if bionic and not DockerFactory.indocker():
            UbuntuInstaller.docker_install()

        MyEnv.state_set("base")

    @staticmethod
    def docker_install():
        if MyEnv.state_get("ubuntu_docker_install"):
            return
        script = """
        apt update
        apt upgrade -y
        apt install sudo python3-pip  -y
        pip3 install pudb
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
        apt update
        sudo apt install docker-ce -y
        """
        Tools.execute(script, interactive=True)
        MyEnv.state_set("ubuntu_docker_install")

    @staticmethod
    def python_redis_install():
        if MyEnv.state_get("python_redis_install"):
            return

        Tools.log("installing jumpscale tools")

        script = """
        cd /tmp
        apt-get install -y mc wget python3 git tmux python3-distutils python3-psutil
        apt-get install -y build-essential
        #apt-get install -y python3.6-dev
        apt-get install -y redis-server

        """
        Tools.execute(script, interactive=True)
        MyEnv.state_set("python_redis_install")

    @staticmethod
    def apts_list():
        return ["iproute2", "python-ufw", "ufw", "libpq-dev", "iputils-ping", "net-tools"]  # "graphviz"

    @staticmethod
    def apts_install():
        for apt in UbuntuInstaller.apts_list():
            if not MyEnv.state_get("apt_%s" % apt):
                command = "apt-get install -y %s" % apt
                Tools.execute(command, die=True)
                MyEnv.state_set("apt_%s" % apt)

    # def pip3(self):
    #     script="""
    #
    #     cd /tmp
    #     curl -sk https://bootstrap.pypa.io/get-pip.py > /tmp/get-pip.py || die "could not download pip" || return 1
    #     python3 /tmp/get-pip.py  >> ${LogFile} 2>&1 || die "pip install" || return 1
    #     rm -f /tmp/get-pip.py
    #     """
    #     Tools.execute(script,interactive=True)


class JumpscaleInstaller:
    def __init__(self, branch=None):
        if not branch:
            branch = DEFAULTBRANCH
        self.account = "threefoldtech"
        self.branch = branch
        self._jumpscale_repos = [("jumpscaleX", "Jumpscale"), ("digitalmeX", "DigitalMe")]

    def install(self, sandboxed=False, force=False, gitpull=False):

        MyEnv.check_platform()

        if "SSH_Agent" in MyEnv.config and MyEnv.config["SSH_Agent"]:
            MyEnv.sshagent.key_default  # means we will load ssh-agent and help user to load it properly

        BaseInstaller.install(sandboxed=sandboxed, force=force)

        Tools.file_touch(os.path.join(MyEnv.config["DIR_BASE"], "lib/jumpscale/__init__.py"))

        self.repos_get(pull=gitpull)
        self.repos_link()
        self.cmds_link()

        script = """
        set -e
        cd {DIR_BASE}
        source env.sh
        mkdir -p /sandbox/openresty/nginx/logs
        mkdir -p /sandbox/var/log
        kosmos 'j.core.installer_jumpscale.remove_old_parts()'
        kosmos 'j.data.nacl.configure(generate=True,interactive=False)'
        # kosmos --instruct=/tmp/instructions.toml
        kosmos 'j.core.tools.pprint("JumpscaleX init step for nacl (encryption) OK.")'
        """
        Tools.execute(script)

    def remove_old_parts(self):
        tofind = ["DigitalMe", "Jumpscale", "ZeroRobot"]
        for part in sys.path:
            if Tools.exists(part):
                for item in os.listdir(part):
                    for item_tofind in tofind:
                        toremove = os.path.join(part, item)
                        if (
                            item.find(item_tofind) != -1
                            and toremove.find("sandbox") == -1
                            and toremove.find("github") == -1
                        ):
                            Tools.log("found old jumpscale item to remove:%s" % toremove)
                            Tools.delete(toremove)
                        if item.find(".pth") != -1:
                            out = ""
                            for line in Tools.file_text_read(toremove).split("\n"):
                                if line.find("threefoldtech") == -1:
                                    out += "%s\n" % line
                            try:
                                Tools.file_write(toremove, out)
                            except:
                                pass
                            # Tools.shell()
        tofind = ["js_", "js9"]
        for part in os.environ["PATH"].split(":"):
            if Tools.exists(part):
                for item in os.listdir(part):
                    for item_tofind in tofind:
                        toremove = os.path.join(part, item)
                        if (
                            item.startswith(item_tofind)
                            and toremove.find("sandbox") == -1
                            and toremove.find("github") == -1
                        ):
                            Tools.log("found old jumpscale item to remove:%s" % toremove)
                            Tools.delete(toremove)

    def repos_get(self, pull=False):

        for sourceName, _ in self._jumpscale_repos:
            Tools.code_github_get(repo=sourceName, account=self.account, branch=self.branch, pull=pull)

    def repos_link(self):
        """
        link the jumpscale repo's to right location in sandbox
        :return:
        """

        for item, alias in self._jumpscale_repos:
            script = """
            set -e
            mkdir -p {DIR_BASE}/lib/jumpscale
            cd {DIR_BASE}/lib/jumpscale
            rm -f {NAME}
            rm -f {ALIAS}
            ln -s {LOC}/{ALIAS} {ALIAS}
            """
            exists, _, _, _, loc = Tools._code_location_get(repo=item, account=self.account)
            if not exists:
                raise RuntimeError("did not find:%s" % loc)

            # destpath = "/sandbox/lib/jumpscale/{ALIAS}"
            # if os.path.exists(destpath):
            #     continue

            args = {"NAME": item, "LOC": loc, "ALIAS": alias}
            Tools.log(Tools.text_replace("link {LOC}/{ALIAS} to {ALIAS}", args=args))
            Tools.execute(script, args=args)

    def cmds_link(self):
        _, _, _, _, loc = Tools._code_location_get(repo="jumpscaleX", account=self.account)
        for src in os.listdir("%s/cmds" % loc):
            src2 = os.path.join(loc, "cmds", src)
            dest = "%s/bin/%s" % (MyEnv.config["DIR_BASE"], src)
            if not os.path.exists(dest):
                Tools.link(src2, dest, chmod=770)
        Tools.link("%s/install/jsx.py" % loc, "{DIR_BASE}/bin/jsx", chmod=770)
        Tools.execute("cd /sandbox;source env.sh;js_init generate")


class DockerFactory:

    __init = False
    _dockers = {}

    @staticmethod
    def indocker():
        """
        will check if we are in a docker
        :return:
        """
        rc, out, _ = Tools.execute("cat /proc/1/cgroup", die=False, showout=False)
        if rc == 0 and out.find("/docker/") != -1:
            return True
        return False

    @staticmethod
    def _init():
        if not DockerFactory.__init:
            rc, out, _ = Tools.execute("cat /proc/1/cgroup", die=False, showout=False)
            if rc == 0 and out.find("/docker/") != -1:
                print("Cannot continue, trying to use docker tools while we are already in a docker")
                sys.exit(1)

            MyEnv._init()

            if MyEnv.platform() == "linux" and not Tools.cmd_installed("docker"):
                UbuntuInstaller.docker_install()

            if not Tools.cmd_installed("docker"):
                print("Could not find Docker installed")
                sys.exit(1)

    @staticmethod
    def container_get(name, portrange=1, image="despiegk/3bot"):
        if name in DockerFactory._dockers:
            return DockerFactory._dockers[name]
        else:
            return DockerContainer(name=name, portrange=portrange, image=image)

    @staticmethod
    def containers_running():
        names = Tools.execute("docker ps --format='{{json .Names}}'", showout=False, replace=False)[1].split("\n")
        names = [i.strip("\"'") for i in names if i.strip() != ""]
        return names

    @staticmethod
    def containers_names():
        names = Tools.execute("docker container ls -a --format='{{json .Names}}'", showout=False, replace=False)[
            1
        ].split("\n")
        names = [i.strip("\"'") for i in names if i.strip() != ""]
        return names

    @staticmethod
    def image_names():
        names = Tools.execute("docker images --format='{{.Repository}}:{{.Tag}}'", showout=False, replace=False)[
            1
        ].split("\n")
        names = [i.strip("\"'") for i in names if i.strip() != ""]
        return names

    @staticmethod
    def image_remove(name):

        for name_find in DockerFactory.image_names():
            if name_find.find(name) != -1:
                Tools.log("remove container:%s" % name_find)
                Tools.execute("docker rmi -f %s" % name)

    @staticmethod
    def reset(images=True):
        """
        will stop/remove all containers
        if images==True will also stop/remove all images
        :return:
        """
        for name in DockerFactory.containers_names():
            d = DockerFactory.container_get(name)
            d.delete()

        # will get all images based on id
        names = Tools.execute("docker images --format='{{.ID}}'", showout=False, replace=False)[1].split("\n")
        for image_id in names:
            if image_id:
                Tools.execute("docker rmi -f %s" % image_id)


class DockerConfig:
    def __init__(self, name, portrange=None, image=None, sshport=None, startupcmd=None):
        self.name = name
        if portrange:
            self.portrange = portrange
        else:
            self.portrange = 1
        if image:
            self.image = image
        else:
            self.image = "despiegk/3bot"
        if sshport:
            self.sshport = sshport
        else:
            self.sshport = 9000 + int(self.portrange) * 100 + 22
        if startupcmd:
            self.startupcmd = startupcmd
        else:
            self.startupcmd = "/sbin/my_init"

        self.path_vardir = Tools.text_replace("{DIR_BASE}/var/containers/{NAME}", args={"NAME": name})
        self.path_config = "%s/config.toml" % (self.path_vardir)

        self.load()

    def _find_sshport(self, startport):
        while Tools.tcp_port_connection_test("localhost", startport):
            print("TCP PORT:%s occupied, go for new one" % startport)
            startport += 1
        return startport

    def load(self):

        if Tools.exists(self.path_config):
            r = Tools.config_load(self.path_config)
            if r != {}:
                self.__dict__.update(r)
        else:
            self.save()

        a = 8000 + int(self.portrange) * 10
        b = 8004 + int(self.portrange) * 10
        self.portrange_txt = "%s-%s:8000-8004" % (a, b)

    def save(self):
        Tools.config_save(self.path_config, self.__dict__)
        self.load()

    def __str__(self):
        return self.__dict__

    __repr__ = __str__


class DockerContainer:
    def __init__(self, name="default", delete=False, portrange=None, image=None, sshport=None, startupcmd=None):
        """
        if you want to start from scratch use: "phusion/baseimage:master"

        if codedir not specified will use /sandbox/code if exists otherwise ~/code
        """
        DockerFactory._init()
        DockerFactory._dockers[name] = self

        self.config = DockerConfig(name=name, portrange=portrange, image=image, sshport=sshport, startupcmd=startupcmd)

        self.container_exists = name in DockerFactory.containers_names()

        self._wireguard = None

        if delete:
            if self.container_exists:
                self.delete()
            newport = self.config._find_sshport(self.config.sshport)
            if self.config.sshport != newport:
                self.config.sshport = newport
                self.config.save()

        if "SSH_Agent" in MyEnv.config and MyEnv.config["SSH_Agent"]:
            MyEnv.sshagent.key_default  # means we will load ssh-agent and help user to load it properly

    @property
    def _path(self):
        return self.config.path_vardir

    @property
    def image(self):
        return self.config.image

    @property
    def name(self):
        return self.config.name

    def clean(self):
        """
        will import & launch
        we have to reimport and make sure there is nothing mapped to host, then we have to remove files, otherwise there could be leftovers
        the result will be a clean exported image and a clean operational container which can be pushed to e.g. docker hub
        :return:
        """
        imagename = "temp/temp"
        self.export(skip_if_exists=False)  # need to re-export to make sure
        tempcontainer = DockerContainer("temp", delete=True, portrange=2)

        tempcontainer.import_(
            path=self.export_last_image_path, imagename=imagename, start=True, mount_dirs=False, portmap=False
        )
        # WILL CLEANUP
        CMD = """
        cd /
        rm -f /tmp/cleanedup
        find . -name "*.pyc" -exec rm -rf {} \;
        find . -type d -name "__pycache__" -delete
        find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
        find . -name "*.bak" -exec rm -rf {} \;
        rm -f /root/.jsx_history
        rm -f /root/.ssh/*
        rm -rf /root/.cache
        mkdir -p /root/.cache
        rm -rf /bd_build
        rm -rf /var/log
        mkdir -p /var/log
        rm -rf /var/mail
        mkdir -p /var/mail
        rm -rf /tmp
        mkdir -p /tmp
        chmod -R 0777 /tmp
        rm -rf /var/backups
        find . -name "*.bak" -exec rm -rf {} \;
        apt-get clean
        apt-get autoremove --purge
        touch /tmp/cleanedup
        """
        for line in CMD.split("\n"):
            line = line.strip()
            print(" - cleanup:%s" % line)
            tempcontainer.dexec(line)
        tempcontainer.export(overwrite=True, path=self.export_last_image_path)
        tempcontainer.delete()
        DockerFactory.image_remove(imagename)
        self.delete()
        assert self.name not in DockerFactory.containers_names()
        self.import_()

    def install(self, baseinstall=True, mount_dirs=True, portmap=True):
        """

        :param baseinstall: is yes will upgrade the ubuntu
        :param cmd: execute additional command after start
        :param mount_dirs if mounts will be done from host system
        :return:
        """

        # portrange_txt += " -p %s:9999/udp" % (a + 9)  # udp port for wireguard

        args = {}
        args["NAME"] = self.config.name
        if portmap:
            args["PORTRANGE"] = "-p %s" % self.config.portrange_txt
        else:
            args["PORTRANGE"] = ""

        args["PORT"] = self.config.sshport
        args["IMAGE"] = self.config.image

        # NOT NEEDED
        # if ":" not in args["IMAGE"]:
        #     args["IMAGE"] += ":latest"

        if not Tools.exists(self._path):
            Tools.dir_ensure(self._path + "/cfg")
            Tools.dir_ensure(self._path + "/var")
            CONFIG = {}
            for i in [
                "USEGIT",
                "DEBUG",
                "LOGGER_INCLUDE",
                "LOGGER_EXCLUDE",
                "LOGGER_LEVEL",
                "LOGGER_CONSOLE",
                "LOGGER_REDIS",
                "SECRET",
            ]:
                if i in MyEnv.config:
                    CONFIG[i] = MyEnv.config[i]
            Tools.config_save(self._path + "/cfg/jumpscale_config.toml", CONFIG)
            shutil.copytree(Tools.text_replace("{DIR_BASE}/cfg/keys", args=args), self._path + "/cfg/keys")

        if not self.container_exists:

            MOUNTS = ""
            if mount_dirs:
                MOUNTS = """
                -v {DIR_CODE}:/sandbox/code \
                -v {DIR_BASE}/var/containers/{NAME}/var:/sandbox/var \
                -v {DIR_BASE}/var/containers/{NAME}/cfg:/sandbox/cfg \
                -v {DIR_BASE}/var/containers/shared:/sandbox/myhost \
                """

            args["MOUNTS"] = Tools.text_replace(MOUNTS.strip(), args=args)
            args["CMD"] = self.config.startupcmd
            if self.name == "3bot":
                args["UDP"] = "-p 7777:7777/udp"
            else:
                args["UDP"] = ""  # for now only name 3bot does it
            run_cmd = (
                "docker run --name={NAME} --hostname={NAME} -d -p {PORT}:22 {UDP} {PORTRANGE} \
            --device=/dev/net/tun --cap-add=NET_ADMIN --cap-add=SYS_ADMIN --cap-add=DAC_OVERRIDE \
            --cap-add=DAC_READ_SEARCH {MOUNTS} {IMAGE} {CMD}".strip()
                .replace("  ", " ")
                .replace("  ", " ")
                .replace("  ", " ")
                .replace("  ", " ")
            )
            run_cmd2 = Tools.text_replace(run_cmd, args=args)

            print(" - Docker machine gets created: ")
            Tools.execute(run_cmd2, interactive=False)

            self.dexec("rm -f /root/.BASEINSTALL_OK")
            print(" - Docker machine OK")
            print(" - Start SSH server")
        else:
            if self.name not in DockerFactory.containers_running():
                Tools.execute("docker start %s" % self.name)
                if not self.name in DockerFactory.containers_running():
                    print("could not start container:%s" % self.name)
                    sys.exit(1)
                self.dexec("rm -f /root/.BASEINSTALL_OK")

        installed = False
        try:
            self.dexec("cat /root/.BASEINSTALL_OK")
            installed = True
        except:
            pass
        if not installed:
            self.dexec("rm -f /root/.BASEINSTALL_OK")
            SSHKEYS = Tools.execute("ssh-add -L", die=False, showout=False)[1]
            if SSHKEYS.strip() != "":
                self.dexec('echo "%s" > /root/.ssh/authorized_keys' % SSHKEYS)

            self.dexec("/usr/bin/ssh-keygen -A")
            self.dexec("/etc/init.d/ssh start")
            self.dexec("rm -f /etc/service/sshd/down")
            if baseinstall:
                print(" - Upgrade ubuntu")
                self.dexec("apt update")
                self.dexec("DEBIAN_FRONTEND=noninteractive apt-get -y upgrade")
                print(" - Upgrade ubuntu ended")
                self.dexec("apt install mc git -y")

            Tools.execute("rm -f ~/.ssh/known_hosts")  # dirty hack

            self.dexec("touch /root/.BASEINSTALL_OK")

    def dexec(self, cmd, interactive=False):
        if "'" in cmd:
            cmd = cmd.replace("'", '"')
        if interactive:
            cmd2 = "docker exec -ti %s bash -c '%s'" % (self.name, cmd)
        else:
            cmd2 = "docker exec -t %s bash -c '%s'" % (self.name, cmd)
        Tools.execute(cmd2, interactive=interactive, showout=True, replace=False, asfile=True)

    def sshexec(self, cmd):
        if "'" in cmd:
            cmd = cmd.replace("'", '"')
        cmd2 = "ssh -oStrictHostKeyChecking=no -t root@localhost -A -p %s '%s'" % (self.config.sshport, cmd)
        Tools.execute(cmd2, interactive=True, showout=False, replace=False, asfile=True)

    def stop(self):
        if self.name in DockerFactory.containers_running():
            Tools.execute("docker stop %s" % self.name, showout=False)

    def start(self):
        if not self.name in DockerFactory.containers_names():
            print("ERROR: cannot find docker with name:%s, cannot start" % self.name)
            sys.exit(1)
        if not self.name in DockerFactory.containers_running():
            Tools.execute("docker start %s" % self.name, showout=False)
        assert self.name in DockerFactory.containers_running()

    def restart(self):
        self.stop()
        self.start()

    def delete(self):
        self.stop()
        Tools.execute("docker rm -f %s" % self.name, die=False, showout=False)
        self.container_exists = False

    @property
    def export_last_image_path(self):
        dpath = "%s/exports/" % self._path
        if not Tools.exists(dpath):
            return None
        items = os.listdir(dpath)
        if items != []:
            items.sort()
            last = items[-1]
            try:
                version = int(last.replace(".tar", ""))
            except:
                Tools.delete("%s/%s" % (dpath, last))
                return self.export_last_image_path
        else:
            return None
        path = "%s/exports/%s.tar" % (self._path, version)
        return path

    def import_(self, path=None, version=None, imagename="despiegk/3bot", start=True, mount_dirs=True, portmap=True):
        """

        :param path:  if not specified will be /sandbox/var/containers/$name/exports/$version.tar
        :param version: version of the export, if not specified & path not specified will be last in the path
        :param imagename: docker image name as used by docker
        :param start: start the container after import
        :param mount_dirs: do you want to mount the dirs to host
        :param portmap: do you want to do the portmappings (ssh is always mapped)
        :return:
        """
        if not path:
            dpath = "%s/exports/" % self._path
            if not Tools.exists(dpath):
                raise RuntimeError("no exports found in:%s" % dpath)
            if not version:
                items = os.listdir(dpath)
                if items != []:
                    items.sort()
                    last = items[-1]
                    version = int(last.replace(".tar", ""))
                else:
                    raise RuntimeError("no exports found in:%s" % dpath)
            path = "%s/exports/%s.tar" % (self._path, version)

        if not Tools.exists(path):
            print("could not find import file:%s" % path)
            sys.exit(1)

        if not path.endswith(".tar"):
            print("export file needs to end with .tar")
            sys.exit(1)

        self.stop()
        DockerFactory.image_remove(imagename)

        print("import docker:%s to %s, will take a while" % (path, self.name))
        Tools.execute("docker import %s %s" % (path, imagename))
        if start:
            self.config.image = imagename
            self.delete()
            self.install(baseinstall=False, mount_dirs=mount_dirs, portmap=portmap)
            self.start()

    def export(self, path=None, overwrite=True, skip_if_exists=False):
        """
        :param path:  if not specified will be /sandbox/var/containers/$name/exports/$version.tar
        :param version:
        :param overwrite: will remove the version if it exists
        :param skip_if_exists, if True will not export if image found
        :return:
        """
        version = None
        self.export_last_image_path  # to have auto fix for badly expored files
        if not path:
            dpath = "%s/exports/" % self._path
            if not Tools.exists(dpath):
                Tools.dir_ensure(dpath)
            items = os.listdir(dpath)
            if items != []:
                items.sort()
                last = items[-1]
                version = int(last.replace(".tar", ""))
                if not overwrite:
                    version += 1
            else:
                version = 1
            path = "%s/exports/%s.tar" % (self._path, version)
        elif not path.endswith(".tar"):
            print("export file needs to end with .tar")
            sys.exit(1)
        if Tools.exists(path) and overwrite and not skip_if_exists:
            Tools.delete(path)
        if not Tools.exists(path):
            print("export docker:%s to %s, will take a while" % (self.name, path))
            Tools.execute("docker export %s -o %s" % (self.name, path))
        else:
            print("export docker:%s to %s, was already there (export skipped)" % (self.name, path))
        return version

    def jumpscale_install(self, secret=None, privatekey=None, redo=False, wiki=False, pull=False, branch=None):

        args_txt = ""
        if secret:
            args_txt += " --secret='%s'" % secret
        if privatekey:
            args_txt += " --privatekey='%s'" % privatekey
        if redo:
            args_txt += " -r"
        if wiki:
            args_txt += " -w"
        if pull:
            args_txt += " --pull"
        if branch:
            args_txt += " --branch %s" % branch

        dirpath = os.path.dirname(inspect.getfile(Tools))
        if dirpath.startswith(MyEnv.config["DIR_CODE"]):
            cmd = "python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/jsx.py install"
        else:
            print("copy installer over from where I install from")
            for item in ["jsx", "InstallTools.py"]:
                src1 = "%s/%s" % (dirpath, item)
                cmd = "scp -P {} -o StrictHostKeyChecking=no \
                    -o UserKnownHostsFile=/dev/null \
                    -r {} root@localhost:/tmp/".format(
                    self.config.sshport, src1
                )
                Tools.execute(cmd)
            cmd = "cd /tmp;python3 jsx install"
        cmd += args_txt
        print(" - Installing jumpscaleX ")
        self.sshexec("apt install python3-click -y")
        self.sshexec(cmd)

        cmd = """
        apt-get autoclean -y
        apt-get clean -y
        apt-get autoremove -y
        # rm -rf /tmp/*
        # rm -rf /var/log/*
        find / | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
        """
        self.sshexec(cmd)

        k = """

        install succesfull:

        # if you use a container do:
        jsx container-kosmos

        or

        kosmos

        """
        args = {}
        args["port"] = self.config.sshport
        print(Tools.text_replace(k, args=args))

    @property
    def wireguard(self):
        if not self._wireguard:
            self._wireguard = WireGuard(container=self)
        return self._wireguard


class SSHAgentKeyError(Exception):
    pass


class SSHAgent:
    def __init__(self):
        self._inited = False
        self._default_key = None
        self.autostart = True
        self.reset()

    @property
    def ssh_socket_path(self):

        if "SSH_AUTH_SOCK" in os.environ:
            return os.environ["SSH_AUTH_SOCK"]

        socketpath = Tools.text_replace("{DIR_VAR}/sshagent_socket")
        os.environ["SSH_AUTH_SOCK"] = socketpath
        return socketpath

    def _key_name_get(self, name):
        if not name:
            if MyEnv.config["SSH_KEY_DEFAULT"]:
                name = MyEnv.config["SSH_KEY_DEFAULT"]
            elif MyEnv.interactive:
                name = Tools.ask_string("give name for your sshkey")
            else:
                name = "default"
        return name

    def key_generate(self, name=None, passphrase=None, reset=False):
        """
        Generate ssh key

        :param reset: if True, then delete old ssh key from dir, defaults to False
        :type reset: bool, optional
        """
        Tools.log("generate ssh key")
        name = self._key_name_get(name)

        if not passphrase:
            if MyEnv.config["interactive"]:
                passphrase = Tools.ask_password(
                    "passphrase for ssh key to generate, \
                        press enter to skip and not use a passphrase"
                )

        path = Tools.text_replace("{DIR_HOME}/.ssh/%s" % name)
        Tools.Ensure("{DIR_HOME}/.ssh")

        if reset:
            Tools.delete("%s" % path)
            Tools.delete("%s.pub" % path)

        if not Tools.exists(path) or reset:
            if passphrase:
                cmd = 'ssh-keygen -t rsa -f {} -N "{}"'.format(path, passphrase)
            else:
                cmd = "ssh-keygen -t rsa -f {}".format(path)
            Tools.execute(cmd, timeout=10)

            Tools.log("load generated sshkey: %s" % path)
        Tools.shell()

    @property
    def key_default(self):
        """

        kosmos 'print(j.core.myenv.sshagent.key_default)'

        checks if it can find the default key for ssh-agent, if not will ask
        :return:
        """

        def ask_key(key_names):
            if len(key_names) == 1:
                if MyEnv.interactive:
                    if not Tools.ask_yes_no("Ok to use key: '%s' as your default key?" % self.key_names[0]):
                        return None
                name = key_names[0]
            elif len(key_names) == 0:
                print(
                    "Cannot find a possible ssh-key, please load your possible keys in your ssh-agent or have in your homedir/.ssh"
                )
                sys.exit(1)
            else:
                name = Tools.ask_choices("Which is your default sshkey to use", key_names)
            return name

        self._keys  # will fetch the keys if not possible will show error

        sshkey = MyEnv.config["SSH_KEY_DEFAULT"]

        if not sshkey:
            if len(self.key_names) > 0:
                sshkey = ask_key(self.key_names)
        if not sshkey:
            hdir = Tools.text_replace("{DIR_HOME}/.ssh")
            if not Tools.exists(hdir):
                print("cannot find home dir:%s" % hdir)
                sys.exit(1)
            choices = []
            for item in os.listdir(hdir):
                item2 = item.lower()
                if not (
                    item.startswith(".")
                    or item2.endswith(".pub")
                    or item2.endswith(".backup")
                    or item2.endswith(".toml")
                    or item2.endswith(".backup")
                    or item in ["known_hosts"]
                ):
                    choices.append(item)
            sshkey = ask_key(choices)

        if not sshkey in self.key_names:
            self.key_load(name=sshkey)
            assert sshkey in self.key_names

        if MyEnv.config["SSH_KEY_DEFAULT"] != sshkey:
            MyEnv.config["SSH_KEY_DEFAULT"] = sshkey
            MyEnv.config_save()

        return sshkey

    def key_load(self, path=None, name=None, passphrase=None, duration=3600 * 24):
        """
        load the key on path

        :param path: path for ssh-key, can be left empty then we get the default name which will become path
        :param name: is the name of key which is in ~/.ssh/$name, can be left empty then will be default
        :param passphrase: passphrase for ssh-key, defaults to ""
        :type passphrase: str
        :param duration: duration, defaults to 3600*24
        :type duration: int, optional
        :raises RuntimeError: Path to load sshkey on couldn't be found
        :return: name,path
        """

        if name:
            path = Tools.text_replace("{DIR_HOME}/.ssh/%s" % name)
        elif path:
            name = os.path.basename(path)
        else:
            name = self._key_name_get(name)
            path = Tools.text_replace("{DIR_HOME}/.ssh/%s" % name)

        if name in self.key_names:
            return

        if not Tools.exists(path):
            raise RuntimeError("Cannot find path:%sfor sshkey (private key)" % path)

        Tools.log("load ssh key: %s" % path)
        os.chmod(path, 0o600)

        if passphrase:
            Tools.log("load with passphrase")
            C = """
                cd /tmp
                echo "exec cat" > ap-cat.sh
                chmod a+x ap-cat.sh
                export DISPLAY=1
                echo {passphrase} | SSH_ASKPASS=./ap-cat.sh ssh-add -t {duration} {path}
                """.format(
                path=path, passphrase=passphrase, duration=duration
            )
            rc, out, err = Tools.execute(C, showout=True, die=False)
            if rc > 0:
                Tools.delete("/tmp/ap-cat.sh")
                print("Could not load sshkey with passphrase (%s)" % path)
                sys.exit(1)
        else:
            # load without passphrase
            cmd = "ssh-add -t %s %s " % (duration, path)
            rc, out, err = Tools.execute(cmd, showout=True, die=False)
            if rc > 0:
                print("Could not load sshkey without passphrase (%s)" % path)
                sys.exit(1)

        self.reset()

        return name, path

    @property
    def _keys(self):
        """
        """
        if self.__keys is None:
            return_code, out, err = Tools.execute("ssh-add -L", showout=False, die=False, timeout=1)
            if return_code:
                if return_code == 1 and out.find("The agent has no identities") != -1:
                    self.__keys = []
                    return []
                else:
                    # Remove old socket if can't connect
                    if Tools.exists(self.ssh_socket_path):
                        Tools.delete(self.ssh_socket_path)
                        # did not work first time, lets try again
                        return_code, out, err = Tools.execute("ssh-add -L", showout=False, die=False, timeout=1)

            if return_code and self.autostart:
                # ok still issue, lets try to start the ssh-agent if that could be done
                self.start()
                return_code, out, err = Tools.execute("ssh-add -L", showout=False, die=False, timeout=1)
                if return_code == 1 and out.find("The agent has no identities") != -1:
                    self.__keys = []
                    return []

            if return_code:
                return_code, out, err = Tools.execute("ssh-add", showout=False, die=False, timeout=1)
                if out.find("Error connecting to agent: No such file or directory"):
                    raise SSHAgentKeyError("Error connecting to agent: No such file or directory")
                else:
                    raise SSHAgentKeyError("Unknown error in ssh-agent, cannot find")

            keys = [line.split() for line in out.splitlines() if len(line.split()) == 3]
            self.__keys = list(map(lambda key: [key[2], " ".join(key[0:2])], keys))

        return self.__keys

    def reset(self):
        self.__keys = None

    @property
    def available(self):
        """
        Check if agent available (does not mean that the sshkey has been loaded, just checks the sshagent is there)
        :return: True if agent is available, False otherwise
        :rtype: bool
        """
        try:
            self._keys
        except SSHAgentKeyError:
            return False
        return True

    def keys_list(self, key_included=False):
        """
        kosmos 'print(j.clients.sshkey.keys_list())'
        list ssh keys from the agent

        :param key_included: defaults to False
        :type key_included: bool, optional
        :raises RuntimeError: Error during listing of keys
        :return: list of paths
        :rtype: list
        """
        if key_included:
            return self._keys
        else:
            return [i[0] for i in self._keys]

    @property
    def key_names(self):

        return [os.path.basename(i[0]) for i in self._keys]

    @property
    def key_paths(self):

        return [i[0] for i in self._keys]

    def profile_js_configure(self):
        """
        kosmos 'j.clients.sshkey.profile_js_configure()'
        """

        bashprofile_path = os.path.expanduser("~/.profile")
        if not Tools.exists(bashprofile_path):
            Tools.execute("touch %s" % bashprofile_path)

        content = j.sal.fs.readFile(bashprofile_path)
        out = ""
        for line in content.split("\n"):
            if line.find("#JSSSHAGENT") != -1:
                continue
            if line.find("SSH_AUTH_SOCK") != -1:
                continue

            out += "%s\n" % line

        out += "export SSH_AUTH_SOCK=%s" % self.ssh_socket_path
        out = out.replace("\n\n\n", "\n\n")
        out = out.replace("\n\n\n", "\n\n")
        j.sal.fs.writeFile(bashprofile_path, out)

    def start(self):
        """

        start ssh-agent, kills other agents if more than one are found

        :raises RuntimeError: Couldn't start ssh-agent
        :raises RuntimeError: ssh-agent was not started while there was no error
        :raises RuntimeError: Could not find pid items in ssh-add -l
        """

        socketpath = self.ssh_socket_path

        Tools.process_kill_by_by_filter("ssh-agent")

        Tools.delete(socketpath)

        if not Tools.exists(socketpath):
            Tools.log("start ssh agent")
            rc, out, err = Tools.execute("ssh-agent -a %s" % socketpath, die=False, showout=False, timeout=20)
            if rc > 0:
                raise RuntimeError("Could not start ssh-agent, \nstdout:%s\nstderr:%s\n" % (out, err))
            else:
                if not Tools.exists(socketpath):
                    err_msg = "Serious bug, ssh-agent not started while there was no error, " "should never get here"
                    raise RuntimeError(err_msg)

                # get pid from out of ssh-agent being started
                piditems = [item for item in out.split("\n") if item.find("pid") != -1]

                # print(piditems)
                if len(piditems) < 1:
                    Tools.log("results was: %s", out)
                    raise RuntimeError("Cannot find items in ssh-add -l")

                # pid = int(piditems[-1].split(" ")[-1].strip("; "))
                # socket_path = j.sal.fs.joinPaths("/tmp", "ssh-agent-pid")
                # j.sal.fs.writeFile(socket_path, str(pid))

            return

        self.reset()

    def kill(self):
        """
        Kill all agents if more than one is found

        """
        Tools.process_kill_by_by_filter("ssh-agent")
        Tools.delete(self.ssh_socket_path)
        # Tools.delete("/tmp", "ssh-agent-pid"))
        self.reset()


class WireGuard:
    def __init__(self, container=None):
        self.container = container
        self._install()

    def _install(self):
        if not Tools.cmd_installed("wg"):
            if MyEnv.platform() == "linux":
                C = """
                add-apt-repository ppa:wireguard/wireguard
                apt-get update
                apt-get install wireguard -y
                """
                Tools.execute(C)
            elif MyEnv.platform() == "darwin":
                C = "brew install wireguard-tools bash"
                Tools.execute(C)

    def server_start(self):
        if MyEnv.platform() == "linux":
            if not Tools.exists("/sandbox/cfg/wireguard.toml"):
                print("- GENERATE WIREGUARD KEY")
                rc, out, err = Tools.execute("wg genkey", showout=False)
                privkey = out.strip()
                rc, out2, err = Tools.execute("echo %s | wg pubkey" % privkey, showout=False)
                pubkey = out2.strip()
                time.sleep(0.1)
                rc, out3, err = Tools.execute("wg genkey", showout=False)
                privkey2 = out3.strip()
                rc, out4, err = Tools.execute("echo %s | wg pubkey" % privkey2, showout=False)
                pubkey2 = out4.strip()

                config = {}
                config["WIREGUARD_SERVER_PUBKEY"] = pubkey
                config["WIREGUARD_SERVER_PRIVKEY"] = privkey
                config["WIREGUARD_CLIENT_PUBKEY"] = pubkey2
                config["WIREGUARD_CLIENT_PRIVKEY"] = privkey2
                config["WIREGUARD_PORT"] = 7777
                Tools.config_save("/sandbox/cfg/wireguard.toml", config)

            config = Tools.config_load("/sandbox/cfg/wireguard.toml")

            C = """
            [Interface]
            Address = 10.10.10.1/24
            SaveConfig = true
            PrivateKey = {WIREGUARD_SERVER_PRIVKEY}
            ListenPort = {WIREGUARD_PORT}

            [Peer]
            PublicKey = {WIREGUARD_CLIENT_PUBKEY}
            AllowedIPs = 10.10.10.0/24
            """
            path = "/tmp/wg0.conf"
            Tools.file_write(path, Tools.text_replace(C, args=config))
            rc, out, err = Tools.execute("ip link del dev wg0", showout=False, die=False)
            cmd = "wg-quick up %s" % path
            Tools.execute(cmd)
        else:
            raise RuntimeError("cannot start server only supported on linux ")

    def connect(self):
        config_container = Tools.config_load("/sandbox/var/containers/%s/cfg/wireguard.toml" % self.container.name)
        C = """
        [Interface]
        Address = 10.10.10.2/24
        PrivateKey = {WIREGUARD_CLIENT_PRIVKEY}

        [Peer]
        PublicKey = {WIREGUARD_SERVER_PUBKEY}
        Endpoint = localhost:{WIREGUARD_PORT}
        AllowedIPs = 10.10.10.0/24
        PersistentKeepalive = 25
        """
        path = "/tmp/wg0.conf"
        if MyEnv.platform() == "linux":
            Tools.file_write(path, Tools.text_replace(C, args=config_container))
            rc, out, err = Tools.execute("ip link del dev wg0", showout=False, die=False)
            cmd = "/usr/local/bin/bash /usr/local/bin/wg-quick %s" % path
            Tools.execute(cmd)
            Tools.shell()
        else:
            print("WIREGUARD CONFIFURATION:\n\n%s" % Tools.text_replace(C, args=config_container))
