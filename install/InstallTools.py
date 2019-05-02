from __future__ import unicode_literals
import copy
import getpass
# import socket
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
from fcntl import F_GETFL, F_SETFL, fcntl
from os import O_NONBLOCK, read
from pathlib import Path
from subprocess import Popen, check_output
import inspect

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


def my_excepthook(exception_type,exception_obj,tb):
    Tools.log(msg=exception_obj,tb=tb,level=40)
    if MyEnv.debug and traceback and pudb:
        # exception_type, exception_obj, tb = sys.exc_info()
        pudb.post_mortem(tb)
    Tools.pprint("{RED}CANNOT CONTINUE{RESET}")
    sys.exit(1)


import inspect

try:
    import yaml
    def serializer(data):
        return yaml.dump(
            data,
            default_flow_style=False,
            default_style='',
            indent=4,
            line_break="\n")
except:
    try:
        import json
        def serializer(data):
            return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=True)
    except:
        def serializer(data):
            return str(data)


try:
    import redis
except:
    redis = False

if redis:
    class RedisQueue():

        def __init__(self,redis,key):
            self.__db = redis
            self.key = key
            self.empty = False

        def qsize(self):
            '''Return the approximate size of the queue.

            :return: approximate size of queue
            :rtype: int
            '''
            return self.__db.llen(self.key)

        @property
        def empty(self):
            '''Return True if the queue is empty, False otherwise.'''
            return self.qsize() == 0

        def reset(self):
            '''
            make empty
            :return:
            '''
            while self.empty == False:
                if self.get_nowait()==None:
                    self.empty = True

        def put(self, item):
            '''Put item into the queue.'''
            self.__db.rpush(self.key, item)

        def get(self, timeout=20):
            '''Remove and return an item from the queue.'''
            if timeout > 0:
                item = self.__db.blpop(self.key, timeout=timeout)
                if item:
                    item = item[1]
            else:
                item = self.__db.lpop(self.key)
            return item

        def fetch(self, block=True, timeout=None):
            '''Return an item from the queue without removing'''
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

        def __init__(self,*args,**kwargs):
            redis.Redis.__init__(self,*args,**kwargs)
            self._storedprocedures_to_sha = {}

        # def dict_get(self, key):
        #     return RedisDict(self, key)

        def queue_get(self, key):
            '''get redis queue
            '''
            return RedisQueue(self, key)

        def storedprocedure_register(self, name, nrkeys, path_or_content):
            '''create stored procedure from path

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

            there is also storedprocedures_sha -> sha without having to decode json

            tips on lua in redis:
            https://redis.io/commands/eval

            '''



            if "\n" not in path_or_content:
                f = open(path_or_content, "r")
                lua = f.read()
                path = path_or_content
            else:
                lua = path_or_content
                path = ""

            script =  self.register_script(lua)

            dd = {}
            dd["sha"] = script.sha
            dd["script"] = lua
            dd["nrkeys"] = nrkeys
            dd["path"] = path

            data = json.dumps(dd)

            self.hset("storedprocedures",name,data)
            self.hset("storedprocedures_sha",name,script.sha)

            self._storedprocedures_to_sha = {}

            # sha = self._sp_data(name)["sha"]
            # assert self.script_exists(sha)[0]

            return script

        def storedprocedure_delete(self, name):
            self.hdel("storedprocedures",name)
            self.hdel("storedprocedures_sha",name)
            self._storedprocedures_to_sha = {}

        @property
        def _redis_cli_path(self):
            if not self.__class__._redis_cli_path_:
                if Tools.cmd_installed("redis-cli_"):
                    self.__class__._redis_cli_path_ =  "redis-cli_"
                else:
                    self.__class__._redis_cli_path_ =  "redis-cli"
            return self.__class__._redis_cli_path_

        def redis_cmd_execute(self,command,debug=False,debugsync=False,keys=[],args=[]):
            """

            :param command:
            :param args:
            :return:
            """
            rediscmd = self._redis_cli_path
            if debug:
                rediscmd+= " --ldb"
            elif debugsync:
                rediscmd+= " --ldb-sync-mode"
            rediscmd+= " --%s"%command
            for key in keys:
                rediscmd+= " %s"%key
            if len(args)>0:
                rediscmd+= " , "
                for arg in args:
                    rediscmd+= " %s"%arg
            # print(rediscmd)
            _,out,_ = Tools.execute(rediscmd,interactive=True)
            return out

        def _sp_data(self,name):
            if name not in self._storedprocedures_to_sha:
                data = self.hget("storedprocedures",name)
                data2 = json.loads(data)
                self._storedprocedures_to_sha[name] = data2
            return self._storedprocedures_to_sha[name]

        def storedprocedure_execute(self,name,*args):
            """

            :param name:
            :param args:
            :return:
            """

            data = self._sp_data(name)
            sha = data["sha"]#.encode()
            assert isinstance(sha, (str))
            # assert isinstance(sha, (bytes, bytearray))
            Tools.shell()
            return self.evalsha(sha,data["nrkeys"],*args)
            # self.eval(data["script"],data["nrkeys"],*args)
            # return self.execute_command("EVALSHA",sha,data["nrkeys"],*args)

        def storedprocedure_debug(self,name,*args):
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
            if path =="":
                from pudb import set_trace; set_trace()

            nrkeys = data['nrkeys']
            args2 = args[nrkeys:]
            keys = args[:nrkeys]

            out = self.redis_cmd_execute("eval %s"%path,debug=True,keys=keys,args=args2)

            return out


class Tools:

    _supported_editors = ["micro","mcedit","joe","vim","vi"]  #DONT DO AS SET  OR ITS SORTED
    j = None
    _shell = None

    @staticmethod
    def traceback_text_get(tb=None,stdout=False):
        """
        format traceback to readable text
        :param tb:
        :return:
        """
        if tb is None:
            tb = sys.last_traceback
        out=""
        for item in traceback.extract_tb(tb):
            fname =  item.filename
            if len(fname)>60:
                fname=fname[-60:]
            line= "%-60s : %-4s: %s"%(fname, item.lineno,item.line)
            if stdout:
                line2 = "        {GRAY}%-60s :{RESET} %-4s: "%(fname, item.lineno)
                Tools.pprint(line2,end="",log=False)
                if pygments_formatter is not False:
                    print(pygments.highlight(item.line ,pygments_pylexer, pygments_formatter).rstrip())
                else:
                    Tools.pprint(item.line,log=False)

            out+="%s\n"%line
        return out

    @staticmethod
    def log(msg,cat="",level=10,data=None,context=None,_deeper=False,stdout=True,redis=True,tb=None,data_show=True):
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
        if isinstance(msg,Exception):
            Tools.pprint("\n\n{BOLD}{RED}EXCEPTION{RESET}\n")
            msg="{RED}EXCEPTION: {RESET}%s"%str(msg)
            level = 50
            if cat is "":
                cat="exception"
        if tb:
            if tb.tb_next is not None:
                frame_ = tb.tb_next.tb_frame
            else:
                # extype, value, tb = sys.exc_info()
                frame_ = tb.tb_frame
            if data is None:
                data = Tools.traceback_text_get(tb,stdout=True)
                data_show = False
            else:
                msg+="\n%s"%Tools.traceback_text_get(tb,stdout=True)
            print()
        else:
            if _deeper:
                frame_ = inspect.currentframe().f_back
            else:
                frame_ = inspect.currentframe().f_back.f_back

        fname = frame_.f_code.co_filename.split("/")[-1]
        defname = frame_.f_code.co_name
        linenr= frame_.f_code.co_firstlineno

        logdict={}
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

        if data and isinstance(data,dict):
            if "password" in data or "secret" in data or "passwd" in data:
                data["password"]="***"

        logdict["data"] = data

        if stdout:
            Tools.log2stdout(logdict,data_show=data_show)

    @staticmethod
    def redis_client_get(addr='localhost',port=6379, unix_socket_path="/sandbox/var/redis.sock",die=True):

        if not redis:
            if die:
                raise RuntimeError("redis python lib not installed, do pip3 install redis")
            else:
                return None
        try:
            cl = Redis(unix_socket_path=unix_socket_path, db=0)
            cl.ping()
        except Exception as e:
            cl = None
            if addr == "" and die:
                raise e
        else:
            return cl

        try:
            cl = Redis(host=addr, port=port, db=0)
            cl.ping()
        except Exception as e:
            if die:
                raise e
            cl = None

        return cl

    @staticmethod
    def _isUnix():
        return 'posix' in sys.builtin_module_names

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
    def _execute_interactive(cmd=None, args=None, die=True,original_command=None):

        if args is None:
            args = cmd.split(" ")
        # else:
        #     args[0] = shutil.which(args[0])

        returncode = os.spawnlp(os.P_WAIT, args[0], *args)
        cmd=" ".join(args   )
        if returncode == 127:
            Tools.shell()
            raise RuntimeError('{0}: command not found\n'.format(args[0]))
        if returncode>0 and returncode != 999:
            if die:
                if original_command:
                    raise RuntimeError("***ERROR EXECUTE INTERACTIVE:\nCould not execute:%s\nreturncode:%s\n"%(original_command,returncode))
                else:
                    raise RuntimeError("***ERROR EXECUTE INTERACTIVE:\nCould not execute:%s\nreturncode:%s\n"%(cmd,returncode))
            return returncode
        return returncode

    @staticmethod
    def file_touch(path):
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)

        with open(path, 'a'):
            os.utime(path, None)

    @staticmethod
    def file_edit(path):
        """
        starts the editor micro with file specified
        """
        user_editor = os.environ.get('EDITOR')
        if user_editor and Tools.cmd_installed(user_editor):
            Tools._execute_interactive("%s %s" % (user_editor, path))
            return
        for editor in Tools._supported_editors:
            if Tools.cmd_installed(editor):
                Tools._execute_interactive("%s %s" % (editor, path))
                return
        raise RuntimeError("cannot edit the file: '{}', non of the supported editors is installed".format(path))



    @staticmethod
    def file_write(path, content,replace=False,args=None):
        if args is None:
            args={}
        dirname = os.path.dirname(path)
        os.makedirs(dirname,exist_ok=True)
        p=Path(path)
        if replace:
            content = Tools.text_replace(content,args=args)
        p.write_text(content)

    @staticmethod
    def file_text_read(path):
        path = Tools.text_replace(path)
        p=Path(path)
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
    def delete(path):
        """Remove a File/Dir/...
        @param path: string (File path required to be removed)
        """
        path = Tools.text_replace(path)
        if MyEnv.debug:
            Tools.log('Remove file with path: %s' % path)
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
        if parts[-1] == '':
            parts = parts[:-1]
        parts = parts[:-1]
        if parts == ['']:
            return os.sep
        return os.sep.join(parts)

    @staticmethod
    def exists(path, followlinks=True):
        """Check if the specified path exists
        @param path: string
        @rtype: boolean (True if path refers to an existing path)
        """
        if path is None:
            raise TypeError('Path is not passed in system.fs.exists')
        found = False
        try:
            st = os.lstat(path)
            found = True
        except (OSError, AttributeError):
            pass
        if found and followlinks and stat.S_ISLNK(st.st_mode):
            if MyEnv.debug:
                Tools.log('path %s exists' % str(path.encode("utf-8")))
            linkpath = os.readlink(path)
            if linkpath[0]!="/":
                linkpath = os.path.join(Tools.path_parent(path), linkpath)
            return Tools.exists(linkpath)
        if found:
            return True
        # Tools.log('path %s does not exist' % str(path.encode("utf-8")))
        return False

    @staticmethod
    def _installbase_for_shell():

        if 'darwin' in MyEnv.platform():

            script = """
            pip3 install ipython
            """
            Tools.execute(script, interactive=True)

        else:

            script = """
                if ! grep -Fq "deb http://mirror.unix-solutions.be/ubuntu/ bionic" /etc/apt/sources.list; then
                    echo >> /etc/apt/sources.list
                    echo "# Jumpscale Setup" >> /etc/apt/sources.list
                    echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
                fi
                apt-get update
                apt-get install -y python3-pip locales
                apt-get install -y curl rsync
                apt-get install -y unzip
                pip3 install ipython
                pip3 install pudb
                pip3 install pygments
                locale-gen --purge en_US.UTF-8
            """
            Tools.execute(script, interactive=True)


    @staticmethod
    def clear():
        print(chr(27)+'[2j')
        print('\033c')
        print('\x1bc')

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
                print("\n*** file: %s"%f.filename)
                print("*** function: %s [linenr:%s]\n" % (f.function,f.lineno))


            Tools._shell = InteractiveShellEmbed(banner1= "", exit_msg="")
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
    def text_strip(content, ignorecomments=False,args={},replace=False,executor=None,colors=True):
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
                if line.strip().startswith('#') and not line.strip().startswith("#!"):
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
            content = Tools.text_replace(content=content,args=args,executor=executor,text_strip=False)
        else:
            if colors and "{" in content:
                for key,val in MyEnv.MYCOLORS.items():
                    content = content.replace("{%s}"%key,val)

        return content

    @staticmethod
    def text_replace(content,args=None,executor=None,ignorecomments=False,text_strip=True):
        """

        j.core.tools.text_replace

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
                return '{%s}' % key

        if args is None:
            args={}

        if "{" in content:

            if args is None:
                args={}

            if executor:
                args.update(executor.config)
            else:
                for key,val in MyEnv.config.items():
                    if key not in args:
                        args[key]=val

            args.update(MyEnv.MYCOLORS)

            replace_args = format_dict(args)
            content = content.format_map(replace_args)

        if text_strip:
            content = Tools.text_strip(content,ignorecomments=ignorecomments,replace=False)

        return content




    @staticmethod
    def log2stdout(logdict,data_show=True):
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
        logdict ["TIME"] = time.strftime(MyEnv.FORMAT_TIME, timetuple)

        if logdict["level"]<11:
            LOGCAT = "DEBUG"
        elif logdict["level"]==15:
            LOGCAT = "STDOUT"
        elif logdict["level"]<21:
            LOGCAT = "INFO"
        elif logdict["level"]<31:
            LOGCAT = "WARNING"
        elif logdict["level"]<41:
            LOGCAT = "ERROR"
        else:
            LOGCAT = "CRITICAL"

        LOGFORMAT = MyEnv.LOGFORMAT[LOGCAT]

        logdict.update(MyEnv.MYCOLORS)

        if len (logdict["filepath"])> 16:
            logdict["filename"] = logdict["filepath"][len(logdict["filepath"])-18:]
        else:
            logdict["filename"] = logdict["filepath"]

        if len (logdict["context"])> 35:
            logdict["context"] = logdict["context"][len(logdict["context"])-34:]
        if logdict["context"].startswith("_"):
            logdict["context"]=""
        elif logdict["context"].startswith(":"):
            logdict["context"]=""


        p = print
        if MyEnv.config.get('log_printer') and MyEnv.config['DEBUG']:
            p = MyEnv.config['log_printer']

        msg=Tools.text_replace(LOGFORMAT,args=logdict)
        msg=Tools.text_replace(msg,args=logdict)
        p(msg)

        if data_show:
            if logdict["data"] not in ["",None,{}]:
                if isinstance(logdict["data"],dict):
                    try:
                        data = serializer(logdict["data"])
                    except Exception as e:
                        data = logdict["data"]
                else:
                    data = logdict["data"]
                data=Tools.text_indent(data,10,strip=True)
                try:
                    data=Tools.text_replace(data,text_strip=False)
                except:
                    pass
                p(data.rstrip())


    @staticmethod
    def pprint(content, ignorecomments=False, text_strip=False,args=None,colors=False,indent=0,end="\n",log=True):
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
            content = Tools.text_replace(content,args=args,text_strip=text_strip,
                                         ignorecomments=ignorecomments)
        elif content.find("{RESET}")!=-1:
            for key,val in MyEnv.MYCOLORS.items():
                content = content.replace("{%s}"%key,val)


        if indent>0:
            content = Tools.text_indent(content)
        if log:
            Tools.log(content,level=15,stdout=False)
        print(content,end=end)

    @staticmethod
    def text_indent(content, nspaces=4, wrap=180, strip=True, indentchar=" ",args=None):
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
        content=str(content)
        if args is not None:
            content = Tools.text_replace(content,args=args)
        if strip:
            content = Tools.text_strip(content,replace=False)
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
        ext=ext.strip(".")
        return Tools.text_replace("/tmp/jumpscale/scripts/{RANDOM}.{ext}",
                                  args={"RANDOM":Tools._random(),"ext":ext})
    @staticmethod
    def _random():
        return str(random.getrandbits(16))

    @staticmethod
    def execute(command, showout=True, useShell=True, cwd=None, timeout=800,die=True,
                async_=False, args=None, env=None,
                interactive=False,self=None,
                replace=True,asfile=False,original_command=None,log=False):

        if env is None:
            env={}
        if self is None:
            self = MyEnv
        command  = Tools.text_strip(command, args=args, replace=replace)
        if "\n" in command or asfile:
            path = Tools._file_path_tmp_get()
            if MyEnv.debug or log:
                Tools.log("execbash:\n'''%s\n%s'''\n" % (path, command))
            command2 = ""
            if die:
                command2 = "set -e\n"
            if cwd:
                command2 += "cd %s\n" % cwd
            command2+=command
            Tools.file_write(path, command2)
            # print(command2)
            command3 = "bash %s" % path
            res = Tools.execute(command3,showout=showout,useShell=useShell,cwd=cwd,
                            timeout=timeout,die=die,env=env,self=self,interactive=interactive,asfile=False,original_command=command )
            Tools.delete(path)
            return res
        else:

            if interactive:
                res = Tools._execute_interactive(cmd=command, die=die,original_command=original_command)
                if MyEnv.debug or log:
                    Tools.log("execute interactive:%s"%command)
                return res
            else:
                if MyEnv.debug or log:
                    Tools.log("execute:%s"%command)

            os.environ["PYTHONUNBUFFERED"] = "1" #WHY THIS???


            # if hasattr(subprocess, "_mswindows"):
            #     mswindows = subprocess._mswindows
            # else:
            #     mswindows = subprocess.mswindows

            if env==None  or env == {}:
                env=os.environ

            if useShell:
                p = Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      close_fds=MyEnv._isUnix(),
                      shell=True, universal_newlines=False, cwd=cwd, bufsize=0, executable='/bin/bash')
            else:
                args = command.split(" ")
                p = Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      close_fds=MyEnv._isUnix(),
                      shell=False, env=env, universal_newlines=False, cwd=cwd, bufsize=0)


            # set the O_NONBLOCK flag of p.stdout file descriptor:
            flags = fcntl(p.stdout, F_GETFL) # get current p.stdout flags
            flags = fcntl(p.stderr, F_GETFL) # get current p.stderr flags
            fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)
            fcntl(p.stderr, F_SETFL, flags | O_NONBLOCK)

            out=""
            err=""

            if async_:
                return p

            def readout(stream):
                if MyEnv._isUnix():
                    # Store all intermediate data
                    data = list()
                    while True:
                        # Read out all available data
                        line = stream.read()
                        if not line:
                            break
                        line=line.decode()#will be utf8
                        # Honour subprocess univeral_newlines
                        if p.universal_newlines:
                            line = p._translate_newlines(line)
                        # Add data to cache
                        data.append(line)
                        if showout:
                            Tools.pprint(line, end="")

                    # Fold cache and return
                    return ''.join(data)

                else:
                    # This is not UNIX, most likely Win32. read() seems to work
                    def readout(stream):
                        line= stream.read().decode()
                        if showout:
                            # Tools.log(line)
                            Tools.pprint(line,end="")


            if timeout < 0:
                out, err = p.communicate()
                out=out.decode()
                err=err.decode()

            else:  # timeout set
                start = time.time()
                end = start + timeout
                now = start

                # if command already finished then read stdout, stderr
                out = readout(p.stdout)
                err = readout(p.stderr)
                while p.poll() is None:
                    #means process is still running

                    time.sleep(0.01)
                    now = time.time()
                    # print("wait")

                    if timeout!=0 and now > end:
                        if Tools._isUnix():
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
                            Tools.log("process killed because of timeout",level=30)
                        return (-2, out, err)

                    # Read out process streams, but don't block
                    out += readout(p.stdout)
                    err += readout(p.stderr)

            rc = -1 if p.returncode < 0 else p.returncode

            if rc<0 or rc>0:
                if MyEnv.debug or log:
                    Tools.log('system.process.run ended, exitcode was %d' % rc)
            # if out!="":
            #     Tools.log('system.process.run stdout:\n%s' % out)
            # if err!="":
            #     Tools.log('system.process.run stderr:\n%s' % err)

            if die and rc!=0:
                msg="\nCould not execute:"
                if command.find("\n") ==-1 and len(command)<40:
                    msg+=" '%s'"%command
                else:
                    command="\n".join(command.split(";"))
                    msg+=Tools.text_indent(command).rstrip()+"\n\n"
                if out.strip()!="":
                    msg+="stdout:\n"
                    msg+=Tools.text_indent(out).rstrip()+"\n\n"
                if err.strip()!="":
                    msg+="stderr:\n"
                    msg+=Tools.text_indent(err).rstrip()+"\n\n"
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
    def ask_choices(msg,choices=[],default=None):
        msg = Tools.text_strip(msg)
        print(msg)
        if "\n" in msg:
            print()
        choices = [str(i) for i in choices if i not in [None,"",","]]
        choices_txt = ",".join(choices)
        mychoice = input("make your choice (%s): "%choices_txt)
        while mychoice not in choices:
            if mychoice.strip() == "" and default:
                return default
            print ("ERROR: only choose %s please"%choices_txt)
            mychoice = input("make your choice (%s): "%choices_txt)
        return mychoice

    @staticmethod
    def ask_yes_no(msg, default='y'):
        """

        :param msg: the msg to show when asking for y or no
        :return: will return True if yes
        """
        return Tools.ask_choices(msg,"y,n",default=default)in ["y",""]

    @staticmethod
    def ask_string(msg,default=None):
        msg = Tools.text_strip(msg)
        print(msg)
        if "\n" in msg:
            print()
        txt = input()
        if default and txt.strip()=="":
            txt = default
        return txt

    @staticmethod
    def cmd_installed(name):
        if not name in MyEnv._cmd_installed:
            MyEnv._cmd_installed[name] =  shutil.which(name) != None
        return MyEnv._cmd_installed[name]

    @staticmethod
    def cmd_args_get():
        res={}
        for i in sys.argv[1:]:
            if "=" in i:
                name,val=i.split("=",1)
                name = name.strip("-").strip().strip("-")
                val = val.strip().strip("'").strip("\"").strip()
                res[name.lower()]=val
            elif i.strip()!="":
                name = i.strip("-").strip().strip("-")
                res[name.lower()]=True
        return res


    @staticmethod
    def _code_location_get(account,repo):
        """
        accountdir will be created if it does not exist yet
        :param repo:
        :param static: static means we don't use git

        :return: repodir_exists,foundgit, accountdir,repodir

            foundgit means, we found .git in the repodir
            dontpull means, we found .dontpull in the repodir, means code is being synced to the repo from remote, should not update

        """
        prefix="code"
        if "DIR_CODE" in MyEnv.config:
            accountdir=os.path.join(MyEnv.config["DIR_CODE"],"github",account)
        else:
            accountdir=os.path.join(MyEnv.config["DIR_BASE"],prefix,"github",account)
        repodir=os.path.join(accountdir,repo)
        gitdir=os.path.join(repodir,".git")
        dontpullloc=os.path.join(repodir,".dontpull")
        if os.path.exists(accountdir):
            if os.listdir(accountdir)==[]:
                shutil.rmtree(accountdir) #lets remove the dir & return it does not exist

        exists = os.path.exists(repodir)
        foundgit = os.path.exists(gitdir)
        dontpull = os.path.exists(dontpullloc)
        return exists,foundgit,dontpull,accountdir,repodir


    @staticmethod
    def code_changed(path):
        """
        check if there is code in there which changed
        :param path:
        :return:
        """
        S="""
        cd {REPO_DIR}
        git diff --exit-code || exit 1
        git diff --cached --exit-code || exit 1
        if git status --porcelain | grep .; then
            exit 1
        else
            exit 0
        fi
        """
        args={}
        args["REPO_DIR"]= path
        rc,out,err = Tools.execute(S,showout=False,die=False, args=args)
        return rc>0

    @staticmethod
    def code_github_get(repo, account="threefoldtech", branch=["master"], pull=True):
        if  MyEnv.sshagent_active_check():
            url = "git@github.com:%s/%s.git"
        else:
            url = "https://github.com/%s/%s.git"

        repo_url = url % (account, repo)
        exists,foundgit,dontpull,ACCOUNT_DIR,REPO_DIR=Tools._code_location_get(account=account,repo=repo)

        args={}
        args["ACCOUNT_DIR"]= ACCOUNT_DIR
        args["REPO_DIR"]= REPO_DIR
        args["URL"] = repo_url
        args["NAME"] = repo
        if isinstance(branch,(list,set)):
            args["BRANCH"] = branch[0]
        else:
            args["BRANCH"] = branch

        if "GITPULL" in os.environ:
            pull = str(os.environ["GITPULL"]) == "1"

        git_on_system = Tools.cmd_installed("git")

        if git_on_system and MyEnv.config["USEGIT"] and ((exists and foundgit) or not exists):
            #there is ssh-key loaded
            #or there is a dir with .git inside and exists
            #or it does not exist yet
            #then we need to use git

            C=""

            if exists==False:
                C="""
                set -e
                mkdir -p {ACCOUNT_DIR}
                """
                Tools.log("get code [git] (first time): %s"%repo)
                Tools.execute(C, args=args,showout=False)
                C = """
                cd {ACCOUNT_DIR}
                git clone  --depth 1 {URL} -b {BRANCH}
                cd {NAME}
                """
                try:
                    Tools.execute(C, args=args,showout=False)
                except Exception as e :
                    C = """
                        cd {ACCOUNT_DIR}
                        git clone  --depth 1 {URL}
                        cd {NAME}
                        """
                    Tools.execute(C, args=args,showout=False)

            else:
                if pull and Tools.code_changed(REPO_DIR):
                    if Tools.ask_yes_no("\n**: found changes in repo '%s', do you want to commit?"%repo):
                        if "GITMESSAGE" in os.environ:
                            args["MESSAGE"] = os.environ["GITMESSAGE"]
                        else:
                            args["MESSAGE"] = input("\nprovide commit message: ")
                            assert args["MESSAGE"].strip() != ""
                    else:
                        sys.exit(1)
                    C="""
                    set -x
                    cd {REPO_DIR}
                    git add . -A
                    git commit -m "{MESSAGE}"
                    git pull

                    """
                    Tools.log("get code & commit [git]: %s"%repo)
                    Tools.execute(C, args=args)
                elif pull:
                    C="""
                    set -x
                    cd {REPO_DIR}
                    git pull
                    """
                    Tools.log("pull code [git]: %s"%repo)
                    Tools.execute(C, args=args)

            def getbranch(args):
                cmd = "cd {REPO_DIR}; git branch | grep \* | cut -d ' ' -f2"
                rc,stdout,err = Tools.execute(cmd, die=False, args=args, interactive=False)
                if rc>0:
                    Tools.shell()
                current_branch = stdout[1].strip()
                Tools.log("Found branch: %s" % current_branch)
                return current_branch

            if pull or exists is False:

                current_branch = getbranch(args=args)

                ok=False
                for branch_item in branch:
                    if ok:
                        continue

                    branch_item = branch_item.strip()

                    if current_branch != branch_item:
                        script="""
                        set -ex
                        cd {REPO_DIR}
                        git checkout {BRANCH} -f
                        exit 999
                        """
                        args["BRANCH"]=branch_item
                        rc,out,err = Tools.execute(script,die=False, args=args,showout=True,interactive=False)
                        if rc==999 or rc==231:
                            ok=True
                    else:
                        ok = True

                getbranch(args=args)

        else:
            Tools.log("get code [zip]: %s"%repo)
            download=False
            if download==False and (not exists or (not dontpull and pull)):

                for branch_item in branch:
                    branch_item = branch_item.strip()
                    url_http="https://github.com/%s/%s/archive/%s.zip"%(account,repo,branch_item)

                    args={}
                    args["ACCOUNT_DIR"]= ACCOUNT_DIR
                    args["REPO_DIR"]= REPO_DIR
                    args["URL"] = url_http
                    args["NAME"] = repo
                    args["BRANCH"] = branch_item

                    script = """
                    set -ex
                    cd {DIR_TEMP}
                    rm -f download.zip
                    curl -L {URL} > download.zip
                    """
                    Tools.execute(script,args=args,die=False)
                    statinfo = os.stat('/tmp/jumpscale/download.zip')
                    if statinfo.st_size < 100000:
                        continue
                    else:
                        script="""
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
                            Tools.execute(script,args=args,die=True)
                        except Exception as e:
                            Tools.shell()
                        download = True

            if not exists and download==False:
                raise RuntimeError("Could not download some code")

    @staticmethod
    def config_load(path="",if_not_exist_create=False,executor=None,content=""):
        """
        only 1 level deep toml format only for int,string,bool
        no multiline

        return dict

        """
        res={}
        if content == "":
            if executor is None:
                if os.path.exists(path):
                    t=Tools.file_text_read(path)
                else:
                    if if_not_exist_create:
                        Tools.config_save(path,{})
                    return {}
            else:
                if executor.exists(path):
                    t=executor.file_read(path)
                else:
                    if if_not_exist_create:
                        Tools.config_save(path,{},executor=executor)
                    return {}
        else:
            t=content

        for line in t.split("\n"):
            if line.strip()=="":
                continue
            if line.startswith("#"):
                continue
            key,val = line.split("=",1)
            if "#" in val:
                val = val.split("#",1)[0]
            key=key.strip().upper()
            val=val.strip().strip("'").strip().strip("\"").strip()
            if str(val).lower() in [0,"false","n","no"]:
                val=False
            elif str(val).lower() in [1,"true","y","yes"]:
                val=True
            elif str(val).find("[")!=-1:
                val2 = str(val).strip("[").strip("]")
                val = [item.strip().strip("'").strip().strip("\"").strip() for item in val2.split(",") if item.strip()!=""]
            else:
                try:
                    val=int(val)
                except:
                    pass
            res[key]=val

        return res

    @staticmethod
    def config_save(path,data,executor=None):
        out=""
        for key,val in data.items():
            key=key.upper()
            if isinstance(val,list):
                val2="["
                for item in val:
                    val2+="'%s',"%item
                val2 = val2.rstrip(",")
                val2+="]"
                val = val2
            elif isinstance(val,str):
                val="'%s'"%val

            if val==True:
                val="true"
            if val==False:
                val="false"
            out+="%s = %s\n"%(key,val)

        if executor:
            executor.file_write(path,out)
        else:
            Tools.file_write(path,out)


LOGFORMATBASE = '{COLOR}{TIME} {filename:<16}{RESET} -{linenr:4d} - {GRAY}{context:<35}{RESET}: {message}'  #DO NOT CHANGE COLOR

class MyEnv():

    _sshagent_active = None
    readonly = False #if readonly will not manipulate local filesystem appart from /tmp
    sandbox_python_active = False   #means we have a sandboxed environment where python3 works in
    sandbox_lua_active = False      #same for lua
    config_changed = False
    _cmd_installed = {}
    state = None
    __init = False
    debug = False

    appname = "installer"

    FORMAT_TIME = "%a %d %H:%M:%S"

    MYCOLORS =   { "RED":"\033[1;31m",
                "BLUE":"\033[1;34m",
                "CYAN":"\033[1;36m",
                "GREEN":"\033[0;32m",
                "GRAY":"\033[0;37m",
                "YELLOW":"\033[0;33m",
                "RESET":"\033[0;0m",
                "BOLD":"\033[;1m",
                "REVERSE":"\033[;7m"}

    LOGFORMAT = {
        'DEBUG':LOGFORMATBASE.replace("{COLOR}","{CYAN}"),
        'STDOUT': '{message}',
        # 'INFO': '{BLUE}* {message}{RESET}',
        'INFO':LOGFORMATBASE.replace("{COLOR}","{BLUE}"),
        'WARNING': LOGFORMATBASE.replace("{COLOR}","{YELLOW}"),
        'ERROR': LOGFORMATBASE.replace("{COLOR}","{RED}"),
        'CRITICAL': '{RED}{TIME} {filename:<16} -{linenr:4d} - {GRAY}{context:<35}{RESET}: {message}',
    }

    db = Tools.redis_client_get(die=False)


    @staticmethod
    def platform():
        """
        will return one of following strings:
            linux, darwin

        """
        return sys.platform

    @staticmethod
    def _isUnix():
        return 'posix' in sys.builtin_module_names

    @staticmethod
    def check_platform():
        """check if current platform is supported (linux or darwin)
        for linux, the version check is done by `UbuntuInstaller.ensure_version()`

        :raises RuntimeError: in case platform is not supported
        """
        platform = MyEnv.platform()
        if 'linux' in platform:
            UbuntuInstaller.ensure_version()
        elif 'darwin' not in platform:
            raise RuntimeError('Your platform is not supported')

    @staticmethod
    def config_default_get(config={}):

        if "HOMEDIR" in os.environ:
            dir_home = os.environ["HOMEDIR"]
        elif "HOME" in os.environ:
            dir_home = os.environ["HOME"]
        else:
            dir_home = "/root"
        config["DIR_HOME"] = dir_home
        config["USEGIT"] = True
        config["DEBUG"] = False

        config["SSH_AGENT"] = False
        config["SSH_KEY_DEFAULT"] = ""

        config["LOGGER_INCLUDE"] = ["*"]
        config["LOGGER_EXCLUDE"] = ["sal.fs"]
        config["LOGGER_LEVEL"] = 15 #means std out & plus gets logged
        config["LOGGER_CONSOLE"] = True
        config["LOGGER_REDIS"] = False

        if MyEnv.readonly:
            config["DIR_TEMP"] = "/tmp/jumpscale_installer"
            config["LOGGER_REDIS"] = False
            config["LOGGER_CONSOLE"] = True

        if not "DIR_TEMP" in config:
            config["DIR_TEMP"] = "/tmp/jumpscale"
        if not "DIR_VAR" in config:
            config["DIR_VAR"] = "%s/var"%config["DIR_BASE"]
        if not "DIR_CODE" in config:
            if MyEnv.readonly:
                config["DIR_CODE"] = "%s/code"%dir_home
            else:
                config["DIR_CODE"] = "%s/code"%config["DIR_BASE"]
        if not "DIR_BIN" in config:
            config["DIR_BIN"] = "%s/bin"%config["DIR_BASE"]
        if not "DIR_APPS" in config:
            config["DIR_APPS"] = "%s/apps"%config["DIR_BASE"]

        return config

    @staticmethod
    def _init():
        if not MyEnv.__init:
            raise RuntimeError("myenv should have been inited by system")

    @staticmethod
    def init(basedir=None,config={},readonly=None,codepath=None,force=False):
        if MyEnv.__init and not force:
            return

        if readonly is not None:
            MyEnv.readonly=readonly

        if basedir is None:
            if Tools.exists("/sandbox"):
                basedir = "/sandbox"
            else:
                #means we did not find a sandbox dir so have to go in readonly mode
                MyEnv.readonly=True

        installpath = os.path.dirname(inspect.getfile(os.path))
        #MEI means we are pyexe BaseInstaller
        if installpath.find("/_MEI")!=-1 or installpath.endswith("dist/install"):
            MyEnv.readonly = True

        if not "DIR_BASE" in config:
            config["DIR_BASE"] = basedir
        if MyEnv.readonly:
            config["DIR_BASE"] = "/tmp/jumpscale"
        if not "DIR_CFG" in config:
            config["DIR_CFG"] = "%s/cfg"%config["DIR_BASE"]

        MyEnv.config_file_path = os.path.join(config["DIR_CFG"],"jumpscale_config.toml")
        MyEnv.state_file_path = os.path.join(config["DIR_CFG"],"jumpscale_done.toml")

        if codepath is not None:
            config["DIR_CODE"]=codepath

        if MyEnv.readonly:
            MyEnv.config = MyEnv.config_default_get(config=config)
        else:
            if os.path.exists(MyEnv.config_file_path):
                MyEnv._config_load(config=config)
            else:
                MyEnv.config = MyEnv.config_default_get(config=config)
                MyEnv.config_save()

        MyEnv.log_includes = [i for i in MyEnv.config.get("LOGGER_INCLUDE",[]) if i.strip().strip("'\'") != ""]
        MyEnv.log_excludes = [i for i in MyEnv.config.get("LOGGER_EXCLUDE",[]) if i.strip().strip("'\'") != ""]
        MyEnv.log_loglevel = MyEnv.config.get("LOGGER_LEVEL",100)
        MyEnv.log_console = MyEnv.config.get("LOGGER_CONSOLE",True)
        MyEnv.log_redis = MyEnv.config.get("LOGGER_REDIS",False)
        MyEnv.debug = MyEnv.config.get("DEBUG",False)

        if os.path.exists(os.path.join(MyEnv.config["DIR_BASE"],"bin","python3.6")):
            MyEnv.sandbox_python_active=True
        else:
            MyEnv.sandbox_python_active=False

        MyEnv._state_load()

        MyEnv.__init = True

    @staticmethod
    def sshagent_active_check():
        """
        check if the ssh agent is active
        :return:
        """
        if MyEnv._sshagent_active is None:
            MyEnv._sshagent_active = len(Tools.execute("ssh-add -L",die=False,showout=False)[1])>40
        return MyEnv._sshagent_active

    @staticmethod
    def sshagent_key_get():
        """
        check if the ssh agent is active
        :return:
        """
        if not MyEnv.sshagent_active_check():
            print("need ssh-agent loaded to be able to find ssh-key to use")
            sys.exit(1)
        return Tools.execute("ssh-add -L",die=False,showout=False)[1].strip().split(" ")[-2].strip()

    @staticmethod
    def config_edit():
        """
        edits the configuration file which is in {DIR_BASE}/cfg/jumpscale_config.toml
        {DIR_BASE} normally is /sandbox
        """
        if MyEnv.readonly:
            raise RuntimeError("config cannot be saved in BaseInstaller only mode")
        Tools.file_edit(MyEnv.config_file_path)

    @staticmethod
    def _config_load(config={}):
        """
        loads the configuration file which is in {DIR_BASE}/cfg/jumpscale_config.toml
        {DIR_BASE} normally is /sandbox
        """
        MyEnv.config = Tools.config_load(MyEnv.config_file_path)
        MyEnv.config.update(config)

    @staticmethod
    def config_save():
        if MyEnv.readonly:
            return
        Tools.config_save(MyEnv.config_file_path,MyEnv.config)

    @staticmethod
    def _state_load():
        """
        only 1 level deep toml format only for int,string,bool
        no multiline
        """
        if MyEnv.state == None:
            if Tools.exists(MyEnv.state_file_path):
                MyEnv.state = Tools.config_load(MyEnv.state_file_path,if_not_exist_create=False)
            elif not MyEnv.readonly:
                MyEnv.state = Tools.config_load(MyEnv.state_file_path,if_not_exist_create=True)
            else:
                MyEnv.state = {}

    @staticmethod
    def state_save():
        if MyEnv.readonly:
            return
        Tools.config_save(MyEnv.state_file_path,MyEnv.state)

    @staticmethod
    def _key_get(key):
        key=key.split("=",1)[0]
        key=key.split(">",1)[0]
        key=key.split("<",1)[0]
        key=key.split(" ",1)[0]
        key=key.upper()
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
    def state_reset(key):
        """
        remove all state
        """
        Tools.delete(MyEnv.state_file_path)
        MyEnv._state_load()


class BaseInstaller():

    @staticmethod
    def install(basedir="/sandbox",config={},sandboxed=False,force=False):

        if not os.path.exists(basedir):
            script = """
            set -ex
            cd /
            sudo mkdir -p {DIR_BASE}/cfg
            sudo chown -R {USERNAME}:{GROUPNAME} {DIR_BASE}
            mkdir -p /usr/local/EGG-INFO
            sudo chown -R {USERNAME}:{GROUPNAME} /usr/local/EGG-INFO
            """
            args={}
            args["DIR_BASE"] = basedir
            args["USERNAME"] = getpass.getuser()
            st = os.stat(MyEnv.config["DIR_HOME"])
            gid = st.st_gid
            args["GROUPNAME"] = grp.getgrgid(gid)[0]
            Tools.execute(script,interactive=True,args=args)

        # MyEnv.init(basedir=basedir,config=config,readonly=False,force=True)

        if force:
            MyEnv.state_delete("install")

        if MyEnv.state_get("install"):
            return #nothing to do

        BaseInstaller.base()
        if MyEnv.platform() == "linux":
            if sandboxed:
                raise RuntimeError("not ok yet")
                UbuntuInstaller.do_all()
            else:
                UbuntuInstaller.base()
        elif "darwin" in MyEnv.platform():
            if sandboxed:
                raise RuntimeError("not ok yet")
                OSXInstaller.do_all()
            else:
                OSXInstaller.base()
        else:
            raise RuntimeError("only OSX and Linux Ubuntu supported.")

        installed = Tools.cmd_installed("git") and Tools.cmd_installed("ssh-agent")
        MyEnv.config["SSH_AGENT"]=installed
        MyEnv.config_save()

        #BASHPROFILE
        if sandboxed:
            env_path = "%s/.bash_profile"%MyEnv.config["DIR_HOME"]
            if Tools.exists(env_path):
                bashprofile = Tools.file_text_read(env_path)
                cmd = "source /sandbox/env.sh"
                if bashprofile.find(cmd)!=-1:
                    bashprofile = bashprofile.replace(cmd,"")
                    Tools.file_write(env_path,bashprofile)
        else:
            #if not sandboxed need to remove old python's from bin dir
            Tools.execute("rm -f {DIR_SANDBOX}/bin/pyth*")
            env_path = "%s/.bash_profile"%MyEnv.config["DIR_HOME"]
            if Tools.exists(env_path):
                bashprofile = Tools.file_text_read(env_path)
                cmd = "source /sandbox/env.sh"
                if bashprofile.find(cmd)==-1:
                    bashprofile+="\n%s\n"%cmd
                    Tools.file_write(env_path,bashprofile)

        Tools.code_github_get(repo="sandbox_base", branch=["master"])

        #will get the sandbox installed
        if not sandboxed:

            script="""
            set -e
            cd {DIR_BASE}
            rsync -ra code/github/threefoldtech/sandbox_base/base/ .

            #remove parts we don't use in in system deployment
            rm -rf {DIR_BASE}/openresty
            rm -rf {DIR_BASE}/lib/python
            rm -rf {DIR_BASE}/lib/pythonbin
            rm -rf {DIR_BASE}/var
            rm -rf {DIR_BASE}/root

            mkdir -p root
            mkdir -p var

            """
            Tools.execute(script,interactive=True)

        else:

            #install the sandbox

            Tools.code_github_get(repo="sandbox_base", branch=["master"])

            script="""
            cd {DIR_BASE}
            rsync -ra code/github/threefoldtech/sandbox_base/base/ .
            mkdir -p root
            """
            Tools.execute(script,interactive=True)

            if MyEnv.platform() == "darwin":
                reponame = "sandbox_osx"
            elif MyEnv.platform() == "linux":
                reponame = "sandbox_ubuntu"
            else:
                raise RuntimeError("cannot install, MyEnv.platform() now found")

            Tools.code_github_get(repo=reponame, branch=["master"])

            script="""
            set -ex
            cd {DIR_BASE}
            rsync -ra code/github/threefoldtech/{REPONAME}/base/ .
            mkdir -p root
            mkdir -p var
            """
            args={}
            args["REPONAME"]=reponame

            Tools.execute(script,interactive=True,args=args)

            script="""
            set -e
            cd {DIR_BASE}
            source env.sh
            python3 -c 'print("- PYTHON OK, SANDBOX USABLE")'
            """
            Tools.execute(script,interactive=True)

            Tools.log("INSTALL FOR BASE OK")

        MyEnv.state_set("install")

    @staticmethod
    def base():
        if MyEnv.state_get("generic_base"):
            return

        if not os.path.exists(MyEnv.config["DIR_TEMP"]):
            os.makedirs(MyEnv.config["DIR_TEMP"],exist_ok=True)

        script="""

        mkdir -p {DIR_TEMP}/scripts
        mkdir -p {DIR_VAR}/log

        """
        Tools.execute(script,interactive=True)
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
                "ipython",
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
                # "pycapnp>=0.5.12",
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
                'ptpython',
                'pygments-markdown-lexer'

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
    def pips_install():
        for pip in BaseInstaller.pips_list(3):

            if not MyEnv.state_get("pip_%s"%pip):
                C="pip3 install --user '%s'"%pip
                Tools.execute(C,die=True)
                MyEnv.state_set("pip_%s"%pip)

class OSXInstaller():

    @staticmethod
    def do_all():
        MyEnv._init()
        Tools.log("installing OSX version")
        pass

    @staticmethod
    def base():
        MyEnv._init()
        if not Tools.cmd_installed("curl") or not Tools.cmd_installed("unzip") or not Tools.cmd_installed("rsync"):
            script="""
            brew install curl unzip rsync
            """
            Tools.execute(script,replace=True)
        BaseInstaller.pips_install()

    @staticmethod
    def brew_uninstall():
        MyEnv._init()
        cmd='sudo ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall)"'
        Tools.execute(cmd,interactive=True)
        toremove = """
        sudo rm -rf /usr/local/.com.apple.installer.keep
        sudo rm -rf /usr/local/include/
        sudo rm -rf /usr/local/etc/
        sudo rm -rf /usr/local/var/
        sudo rm -rf /usr/local/FlashcardService/
        sudo rm -rf /usr/local/texlive/
        """
        Tools.execute(toremove,interactive=True)

class UbuntuInstaller():

    @staticmethod
    def do_all():
        MyEnv._init()
        Tools.log("installing Ubuntu version")

        UbuntuInstaller.ensure_version()
        UbuntuInstaller.base()
        UbuntuInstaller.ubuntu_base_install()
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

        script="""
        if ! grep -Fq "deb http://mirror.unix-solutions.be/ubuntu/ bionic" /etc/apt/sources.list; then
            echo >> /etc/apt/sources.list
            echo "# Jumpscale Setup" >> /etc/apt/sources.list
            echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
        fi
        apt-get update

        apt-get install -y curl rsync unzip
        locale-gen --purge en_US.UTF-8

        """
        Tools.execute(script,interactive=True)
        MyEnv.state_set("base")

    @staticmethod
    def ubuntu_base_install():
        if MyEnv.state_get("ubuntu_base_install"):
            return

        Tools.log("installing base system")

        script="""
        apt-get install -y python3-pip locales
        pip3 install ipython
        """
        Tools.execute(script, interactive=True)
        MyEnv.state_set("ubuntu_base_install")

    @staticmethod
    def docker_install():
        if MyEnv.state_get("ubuntu_docker_install"):
            return
        script="""
        apt update
        apt upgrade -y
        apt install python3-pip  -y
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

        script="""
        cd /tmp
        apt-get install -y mc wget python3 git tmux python3-distutils python3-psutil
        apt-get install -y build-essential python3.6-dev
        pip3 install pycapnp peewee cryptocompare
        apt-get install -y redis-server

        """
        Tools.execute(script, interactive=True)
        MyEnv.state_set("python_redis_install")


    @staticmethod
    def apts_list():
        return [
            'iproute2',
            'python-ufw',
            'ufw',
            'libpq-dev',
            'graphviz',
        ]

    @staticmethod
    def apts_install():
        for apt in UbuntuInstaller.apts_list():
            if not MyEnv.state_get('apt_%s' % apt):
                command = 'apt-get install -y %s' % apt
                Tools.execute(command,die=True)
                MyEnv.state_set('apt_%s' % apt)

    # def pip3(self):
    #     script="""
    #
    #     cd /tmp
    #     curl -sk https://bootstrap.pypa.io/get-pip.py > /tmp/get-pip.py || die "could not download pip" || return 1
    #     python3 /tmp/get-pip.py  >> ${LogFile} 2>&1 || die "pip install" || return 1
    #     rm -f /tmp/get-pip.py
    #     """
    #     Tools.execute(script,interactive=True)

class JumpscaleInstaller():

    def __init__(self, branch=["development"]):
        MyEnv._init()
        self.account = "threefoldtech"
        self.branch = branch
        self._jumpscale_repos = [("jumpscaleX","Jumpscale"), ("digitalmeX","DigitalMe")]

    def install(self,basedir="/sandbox",config={},sandboxed=False,force=False,secret="1234",private_key_words=None,gitpull=True):

        MyEnv.check_platform()

        BaseInstaller.install(basedir=basedir,config=config,sandboxed=sandboxed,force=force)

        Tools.file_touch(os.path.join(MyEnv.config["DIR_BASE"], "lib/jumpscale/__init__.py"))

        if self.branch:
            #TODO: need to check if ok
            self.branch = [i.strip() for i in self.branch.split(",") if i.strip()!=""]

        self.repos_get(pull=gitpull)
        self.repos_link()
        self.cmds_link()

        script="""
        set -e
        cd {DIR_BASE}
        source env.sh
        mkdir -p /sandbox/openresty/nginx/logs
        mkdir -p /sandbox/var/log
        kosmos 'j.core.installer_jumpscale.remove_old_parts()'
        kosmos --instruct=/tmp/instructions.toml
        kosmos 'j.tools.console.echo("JumpscaleX IS OK.")'
        """

        if private_key_words is None:
            private_key_words = "" #will make sure it gets generated

        if secret.lower().strip() == "ssh":
            C="""
            [[instruction]]
            instruction_method = "j.data.nacl.configure"
            name = "default"
            sshagent_use = true
            privkey_words = "{WORDS}"
            generate = true
            """
        else:
            C="""
            [[instruction]]
            instruction_method = "j.data.nacl.configure"
            name = "default"
            sshagent_use = false
            secret = "{SECRET}"
            privkey_words = "{WORDS}"
            generate = true
            """
        kwargs={}
        kwargs["WORDS"] = private_key_words
        kwargs["SECRET"] = secret

        C=Tools.text_strip(C,args=kwargs,replace=True)

        Tools.file_write("/tmp/instructions.toml",C)
        Tools.execute(script)


    def remove_old_parts(self):
        tofind=["DigitalMe","Jumpscale","ZeroRobot"]
        for part in sys.path:
            if Tools.exists(part):
                for item in os.listdir(part):
                    for item_tofind in tofind:
                        toremove =  os.path.join(part,item)
                        if item.find(item_tofind)!=-1  and toremove.find("sandbox")==-1 and toremove.find("github")==-1:
                            Tools.log("found old jumpscale item to remove:%s"%toremove)
                            Tools.delete(toremove)
                        if item.find(".pth")!=-1:
                            out=""
                            for line in Tools.file_text_read(toremove).split("\n"):
                                if line.find("threefoldtech")==-1:
                                    out+="%s\n"%line
                            try:
                                Tools.file_write(toremove,out)
                            except:
                                pass
                            # Tools.shell()
        tofind=["js_","js9"]
        for part in os.environ["PATH"].split(":"):
            if Tools.exists(part):
                for item in os.listdir(part):
                    for item_tofind in tofind:
                        toremove =  os.path.join(part,item)
                        if item.startswith(item_tofind) and toremove.find("sandbox")==-1 and toremove.find("github")==-1:
                                Tools.log("found old jumpscale item to remove:%s"%toremove)
                                Tools.delete(toremove)



    def repos_get(self,pull=True):

        for sourceName,_ in self._jumpscale_repos:
            Tools.code_github_get(repo=sourceName, account=self.account, branch=self.branch, pull=pull)

    def repos_link(self):
        """
        link the jumpscale repo's to right location in sandbox
        :return:
        """

        for item,alias in self._jumpscale_repos:
            script="""
            set -e
            mkdir -p {DIR_BASE}/lib/jumpscale
            cd {DIR_BASE}/lib/jumpscale
            rm -f {NAME}
            rm -f {ALIAS}
            ln -s {LOC}/{ALIAS} {ALIAS}
            """
            exists,_,_,_,loc=Tools._code_location_get(repo=item,account=self.account)
            if not exists:
                raise RuntimeError("did not find:%s"%loc)


            # destpath = "/sandbox/lib/jumpscale/{ALIAS}"
            # if os.path.exists(destpath):
            #     continue

            args={"NAME":item,"LOC":loc,"ALIAS":alias}
            Tools.log(Tools.text_replace("link {LOC}/{ALIAS} to {ALIAS}",args=args))
            Tools.execute(script,args=args)

    def cmds_link(self):

        _,_,_,_,loc=Tools._code_location_get(repo="jumpscaleX",account=self.account)
        for src in os.listdir("%s/cmds" % loc):
            src2=os.path.join(loc,"cmds",src)
            dest="%s/bin/%s" % (MyEnv.config["DIR_BASE"], src)
            if not os.path.exists(dest):
                Tools.execute("ln -s {} {}".format(src2, dest))
                Tools.execute("chmod 770 {}".format(dest))
        Tools.execute("cd /sandbox;source env.sh;js_init generate")


# try:
#     from colored_traceback import add_hook
#     import colored_traceback
#     add_hook()
#     MyEnv._colored_traceback = colored_traceback
# except ImportError:
#     MyEnv._colored_traceback = None

class Docker():

    def __init__(self,name="default",delete=False,portrange=1,image='despiegk/3bot',
                sshkey=None,baseinstall=True):
        """
        if you want to start from scratch use: "phusion/baseimage:master"

        if codedir not specified will use /sandbox/code if exists otherwise ~/code
        """
        rc,out,_=Tools.execute("cat /proc/1/cgroup",die=False,showout=False)
        if rc==0 and out.find("/docker/")!=-1:
            print("Cannot continue, trying to use docker tools while we are already in a docker")
            sys.exit(1)

        MyEnv._init()
        self.name = name

        if not sshkey:
            sshkey = MyEnv.sshagent_key_get()

        if MyEnv.platform()=="linux" and not Tools.cmd_installed("docker"):
            UbuntuInstaller.docker_install()

        if not Tools.cmd_installed("docker"):
            print("Could not find Docker installed")
            sys.exit(1)

        container_exists = name in self.docker_names()

        if container_exists and delete:
            Tools.execute("docker rm -f %s"%name)
            container_exists = False

        a=8000+int(portrange)*10
        b=8004+int(portrange)*10
        portrange_txt="%s-%s:8000-8004"%(a,b)
        portrange_txt +=" -p %s:9999/udp"%(a+9)  #udp port for wireguard

        port = 9000+int(portrange)*100 + 22
        self.port = port

        args={}
        args["NAME"]=name
        args["PORTRANGE"] = "-p %s"%portrange_txt
        args["PORT"] = port
        args["IMAGE"] = image

        if not container_exists:
            cmd="""
            docker run --name {NAME} \
            --hostname {NAME} \
            -d \
            -p {PORT}:22 {PORTRANGE} \
            --device=/dev/net/tun \
            --cap-add=NET_ADMIN --cap-add=SYS_ADMIN \
            --cap-add=DAC_OVERRIDE --cap-add=DAC_READ_SEARCH \
            -v {DIR_CODE}:/sandbox/code {IMAGE}
            """
            print(" - Docker machine gets created: ")
            Tools.execute(cmd,args=args,interactive=True)
            print(" - Docker machine OK")
            print(" - Start SSH server")
        else:
            print(" - Docker machine was already there.")
            if name not in self.docker_running():
                Tools.execute("docker start %s"% name)
                if not name in self.docker_running():
                    print("could not start container:%s"%name)
                    sys.exit(1)

        SSHKEYS = Tools.execute("ssh-add -L",die=False,showout=False)[1]
        if SSHKEYS.strip()!="":
            self.dexec('echo "%s" > /root/.ssh/authorized_keys'%SSHKEYS)

        self.dexec("/usr/bin/ssh-keygen -A")
        self.dexec('/etc/ind/ssh start')
        self.dexec('rm -f /etc/service/sshd/down')
        if baseinstall:
            print(" - Upgrade ubuntu")
            self.dexec('apt update; apt upgrade -y; apt install mc git -y')

        Tools.execute("rm -f ~/.ssh/known_hosts")  # dirty hack


    def dexec(self,cmd,interactive=False):
        if "'" in cmd:
            cmd = cmd.replace("'","\"")
        if interactive:
            cmd2 = "docker exec -ti %s bash -c '%s'"%(self.name,cmd)
        else:
            cmd2 = "docker exec -t %s bash -c '%s'"%(self.name,cmd)
        Tools.execute( cmd2, interactive=interactive,showout=True,replace=False,asfile=True)


    def sshexec(self,cmd):
        if "'" in cmd:
            cmd = cmd.replace("'","\"")
        cmd2 = "ssh -oStrictHostKeyChecking=no -t root@localhost -A -p %s '%s'"%(self.port,cmd)
        Tools.execute(cmd2,interactive=True,showout=False,replace=False,asfile=True)


    def docker_running(self):
        names = Tools.execute("docker ps --format='{{json .Names}}'",showout=False,replace=False)[1].split("\n")
        names = [i.strip("\"'") for i in names if i.strip()!=""]
        return names

    def docker_names(self):
        names = Tools.execute("docker container ls -a --format='{{json .Names}}'",showout=False,replace=False)[1].split("\n")
        names = [i.strip("\"'") for i in names if i.strip()!=""]
        return names

    def image_names(self):
        names = Tools.execute("docker images --format='{{.Repository}}:{{.Tag}}'",showout=False,replace=False)[1].split("\n")
        names = [i.strip("\"'") for i in names if i.strip()!=""]
        return names

    def jumpscale_install(self,secret="1234",private_key="",redo=False,wiki=False):

        args_txt = ""
        args_txt+=" --secret='%s'"%secret
        if private_key:
            args_txt+=" --private_key='%s'"%private_key
        if redo:
            args_txt+=" -r"
        if wiki:
            args_txt+=" -w"
        args_txt+=" -y"

        # args_txt+=" -c"
        # args_txt+=" --debug"

        cmd = "python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py %s"%args_txt
        print(" - Installing jumpscaleX ")
        self.sshexec(cmd)

        dirpath = os.path.dirname(inspect.getfile(Tools))

        for item in ["install.py","3bot_dev.py","InstallTools.py"]:
            src1 = "%s/%s"%(dirpath,item)
            cmd = "scp -P %s %s root@localhost:/tmp/" %(args["port"],src1)
            Tools.execute(cmd)
        cmd = "cd /tmp;python3 3bot_dev.py %s"%args_txt

        print(" - Installing jumpscaleX ")

        cmd="""
        apt-get autoclean
        apt-get clean
        apt-ge autoremove
        rm -rf /tmp/*
        rm -rf /var/log/*
        find / | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
        """
        self.sshexec(cmd)


        k = """

        install succesfull:

        # to login to the docker using ssh use (if std port)
        ssh root@localhost -A -p {port}

        #to login & automatically use the shell
        ssh root@localhost -A -p {port} 'source /sandbox/env.sh;kosmos'

        will now login automatically

        """
        print(Tools.text_replace(k,args=args))

        cmd = "ssh root@localhost -A -p %s 'source /sandbox/env.sh;kosmos'"%args["port"]
        Tools.shell()
