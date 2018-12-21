import copy
import getpass
# import socket
import grp
import logging
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


# Returns escape codes from format codes
def esc(*x):
    return '\033[' + ';'.join(x) + 'm'


# The initial list of escape codes
escape_codes = {
    'reset': esc('0'),
    'bold': esc('01'),
    'thin': esc('02')
}

# The color names
COLORS = [
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'purple',
    'cyan',
    'white'
]

PREFIXES = [
    # Foreground without prefix
    ('3', ''), ('01;3', 'bold_'), ('02;3', 'thin_'),

    # Foreground with fg_ prefix
    ('3', 'fg_'), ('01;3', 'fg_bold_'), ('02;3', 'fg_thin_'),

    # Background with bg_ prefix - bold/light works differently
    ('4', 'bg_'), ('10', 'bg_bold_'),
]

for prefix, prefix_name in PREFIXES:
    for code, name in enumerate(COLORS):
        escape_codes[prefix_name + name] = esc(prefix + str(code))


def parse_colors(sequence):
    """Return escape codes from a color sequence."""
    return ''.join(escape_codes[n] for n in sequence.split(',') if n)


__all__ = ('escape_codes', 'default_log_colors', 'ColoredFormatter',
           'LevelFormatter', 'TTYColoredFormatter')

# The default colors to use for the debug levels
default_log_colors = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

# The default format to use for each style
default_formats = {
    '%': '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    '{': '{log_color}{levelname}:{name}:{message}',
    '$': '${log_color}${levelname}:${name}:${message}'
}


class ColoredRecord(object):
    """
    Wraps a LogRecord, adding named escape codes to the internal dict.

    The internal dict is used when formatting the message (by the PercentStyle,
    StrFormatStyle, and StringTemplateStyle classes).
    """

    def __init__(self, record):
        """Add attributes from the escape_codes dict and the record."""
        self.__dict__.update(escape_codes)
        self.__dict__.update(record.__dict__)

        # Keep a reference to the original record so ``__getattr__`` can
        # access functions that are not in ``__dict__``
        self.__record = record

    def __getattr__(self, name):
        return getattr(self.__record, name)


class ColoredFormatter(logging.Formatter):
    """
    A formatter that allows colors to be placed in the format string.

    Intended to help in creating more readable logging output.
    """

    def __init__(self, fmt=None, datefmt=None, style='%',
                 log_colors=None, reset=True,
                 secondary_log_colors=None):
        """
        Set the format and colors the ColoredFormatter will use.

        The ``fmt``, ``datefmt`` and ``style`` args are passed on to the
        ``logging.Formatter`` constructor.

        The ``secondary_log_colors`` argument can be used to create additional
        ``log_color`` attributes. Each key in the dictionary will set
        ``{key}_log_color``, using the value to select from a different
        ``log_colors`` set.

        :Parameters:
        - fmt (str): The format string to use
        - datefmt (str): A format string for the date
        - log_colors (dict):
            A mapping of log level names to color names
        - reset (bool):
            Implicitly append a color reset to all records unless False
        - style ('%' or '{' or '$'):
            The format style to use. (*No meaning prior to Python 3.2.*)
        - secondary_log_colors (dict):
            Map secondary ``log_color`` attributes. (*New in version 2.6.*)
        """
        if fmt is None:
            if sys.version_info > (3, 2):
                fmt = default_formats[style]
            else:
                fmt = default_formats['%']

        if sys.version_info > (3, 2):
            super(ColoredFormatter, self).__init__(fmt, datefmt, style)
        elif sys.version_info > (2, 7):
            super(ColoredFormatter, self).__init__(fmt, datefmt)
        else:
            logging.Formatter.__init__(self, fmt, datefmt)

        self.log_colors = (
            log_colors if log_colors is not None else default_log_colors)
        self.secondary_log_colors = secondary_log_colors
        self.reset = reset

    def color(self, log_colors, level_name):
        """Return escape codes from a ``log_colors`` dict."""
        return parse_colors(log_colors.get(level_name, ""))

    def format(self, record):
        """Format a message from a record object."""
        record = ColoredRecord(record)
        record.log_color = self.color(self.log_colors, record.levelname)

        # Set secondary log colors
        if self.secondary_log_colors:
            for name, log_colors in self.secondary_log_colors.items():
                color = self.color(log_colors, record.levelname)
                setattr(record, name + '_log_color', color)

        # Format the message
        if sys.version_info > (2, 7):
            message = super(ColoredFormatter, self).format(record)
        else:
            message = logging.Formatter.format(self, record)

        # Add a reset code to the end of the message
        # (if it wasn't explicitly added in format str)
        if self.reset and not message.endswith(escape_codes['reset']):
            message += escape_codes['reset']

        return message


class LevelFormatter(ColoredFormatter):
    """An extension of ColoredFormatter that uses per-level format strings."""

    def __init__(self, fmt=None, datefmt=None, style='%',
                 log_colors=None, reset=True,
                 secondary_log_colors=None):
        """
        Set the per-loglevel format that will be used.

        Supports fmt as a dict. All other args are passed on to the
        ``colorlog.ColoredFormatter`` constructor.

        :Parameters:
        - fmt (dict):
            A mapping of log levels (represented as strings, e.g. 'WARNING') to
            different formatters. (*New in version 2.7.0)
        (All other parameters are the same as in colorlog.ColoredFormatter)

        Example:

        formatter = colorlog.LevelFormatter(fmt={
            'DEBUG':'%(log_color)s%(msg)s (%(module)s:%(lineno)d)',
            'INFO': '%(log_color)s%(msg)s',
            'WARNING': '%(log_color)sWARN: %(msg)s (%(module)s:%(lineno)d)',
            'ERROR': '%(log_color)sERROR: %(msg)s (%(module)s:%(lineno)d)',
            'CRITICAL': '%(log_color)sCRIT: %(msg)s (%(module)s:%(lineno)d)',
        })
        """
        if sys.version_info > (2, 7):
            super(LevelFormatter, self).__init__(
                fmt=fmt, datefmt=datefmt, style=style, log_colors=log_colors,
                reset=reset, secondary_log_colors=secondary_log_colors)
        else:
            ColoredFormatter.__init__(
                self, fmt=fmt, datefmt=datefmt, style=style,
                log_colors=log_colors, reset=reset,
                secondary_log_colors=secondary_log_colors)
        self.style = style
        self.fmt = fmt

    def format(self, record):
        """Customize the message format based on the log level."""
        if isinstance(self.fmt, dict):
            self._fmt = self.fmt[record.levelname]
            if sys.version_info > (3, 2):
                # Update self._style because we've changed self._fmt
                # (code based on stdlib's logging.Formatter.__init__())
                if self.style not in logging._STYLES:
                    raise ValueError('Style must be one of: %s' % ','.join(
                        logging._STYLES.keys()))
                self._style = logging._STYLES[self.style][0](self._fmt)

        if sys.version_info > (2, 7):
            message = super(LevelFormatter, self).format(record)
        else:
            message = ColoredFormatter.format(self, record)

        return message


class TTYColoredFormatter(ColoredFormatter):
    """
    Blanks all color codes if not running under a TTY.

    This is useful when you want to be able to pipe colorlog output to a file.
    """

    def __init__(self, *args, **kwargs):
        """Overwrite the `reset` argument to False if stream is not a TTY."""
        self.stream = kwargs.pop('stream', sys.stdout)

        # Both `reset` and `isatty` must be true to insert reset codes.
        kwargs['reset'] = kwargs.get('reset', True) and self.stream.isatty()

        ColoredFormatter.__init__(self, *args, **kwargs)

    def color(self, log_colors, level_name):
        """Only returns colors if STDOUT is a TTY."""
        if not self.stream.isatty():
            log_colors = {}
        return ColoredFormatter.color(self, log_colors, level_name)

#see https://github.com/borntyping/python-colorlog
class LogFormatter(TTYColoredFormatter):

    def __init__(self, fmt=None, datefmt=None, style="{"):
        if fmt is None:
            fmt = MyEnv.FORMAT_LOG
        if datefmt is None:
            datefmt = MyEnv.FORMAT_TIME
        super(LogFormatter, self).__init__(
            fmt=fmt,
            datefmt=datefmt,
            reset=False,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style=style)
        self.length = 20

    def format(self, record):
        if len(record.pathname) > self.length:
            record.pathname = "..." + record.pathname[-self.length:]
        return super(LogFormatter, self).format(record)


class Tools():
    @staticmethod
    def log(msg):
        logging.debug(msg)

    @staticmethod
    def _isUnix():
        return 'posix' in sys.builtin_module_names

    @staticmethod
    def error_raise(msg, pythonerror=None):
        print ("** ERROR **")
        Tools.log(msg)
        # sys.exit(1)
        raise RuntimeError(msg)

    @staticmethod
    def _execute_interactive(cmd=None, args=None, die=True):
        if args is None:
            args = cmd.split(" ")
        if interactive:
            returncode = os.spawnvpe(os.P_WAIT, args[0], args, os.environ)
            cmd=" ".join(args   )
            if returncode == 127:
                Tools.error_raise('{0}: command not found\n'.format(args[0]))
            if returncode>0 and returncode != 999:
                if die:
                    Tools.error_raise("***ERROR EXECUTE INTERACTIVE:\nCould not execute:%s\nreturncode:%s\n"%(cmd,returncode))
                return returncode
            return returncode

    @staticmethod
    def file_touch(path):
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)

        with open(path, 'a'):
            os.utime(path, None)

    @staticmethod
    def file_write(path, content,replace=False,args=None):
        if args is None:
            args={}
        dirname = os.path.dirname(path)
        os.makedirs(dirname,exist_ok=True)
        p=Path(path)
        if replace:
            content = Tools.text_replace(content,args=args)
        res=p.write_text(content)

    @staticmethod
    def file_text_read(path):
        p=Path(path)
        try:
            return p.read_text()
        except Exception as e:
            Tools.shell()

    @staticmethod
    def delete(path):
        """Remove a File/Dir/...
        @param path: string (File path required to be removed)
        """
        logger.debug('Remove file with path: %s' % path)
        if os.path.islink(path):
            os.unlink(path)
        if not Tools.exists(path):
            return
        if os.path.isfile(path):
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
            logger.debug('path %s exists' % str(path.encode("utf-8")))
            linkpath = os.readlink(path)
            if linkpath[0]!="/":
                linkpath = os.path.join(Tools.path_parent(path), linkpath)
            return Tools.exists(linkpath)
        if found:
            return True
        logger.debug('path %s does not exist' % str(path.encode("utf-8")))
        return False

    @staticmethod
    def _installbase_for_shell(self):

        script="""
        echo >> /etc/apt/sources.list
        echo "# Jumpscale Setup" >> /etc/apt/sources.list
        echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
        apt-get update

        apt-get install -y python3-pip locales
        apt-get install -y curl rsync
        apt-get install -y unzip
        pip3 install ipython
        locale-gen --purge en_US.UTF-8
        """
        Tools.execute(script, interactive=True)

        MyEnv.state_set("ubuntu_base_install")

    @staticmethod
    def shell(loc=True):
        try:
            from IPython.terminal.embed import InteractiveShellEmbed
        except:
            Tools._installbase()
        _shell = InteractiveShellEmbed(banner1= "", exit_msg="")
        if loc:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            f = calframe[1]
            print("\n*** file: %s"%f.filename)
            print("*** function: %s [linenr:%s]\n" % (f.function,f.lineno))
        return _shell(stack_depth=2)

    @staticmethod
    def text_strip(content, ignorecomments=True,args={},replace=True,executor=None):
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
            content = Tools.text_replace(content,args=args,executor=executor)

        return content

    @staticmethod
    def text_replace(content,args=None,executor=None):
        """

        j.core.tools.text_replace

        args will be substitued to .format(...) string function https://docs.python.org/3/library/string.html#formatspec
        MyEnv.config will also be given to the format function

        content example:

        "{name!s:>10} {val} {n:<10.2f}"  #floating point rounded to 2 decimals

        performance is +100k per sec



        """
        if args is None:
            args={}

        if "{" in content:
            if executor:
                args.update(executor.config)
            else:
                args.update(MyEnv.config)
            content = content.format(**args)

        return content


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
        if args is not None:
            content = Tools.text_replace(content,args=args)
        if strip:
            content = Tools.text_strip(content)
        if wrap > 0:
            content = Tools.text_wrap(content, wrap)
            # flatten = True
        if content is None:
            return
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
    def execute(command, showout=True, useShell=True, cwd=None, timeout=600,die=True,
                async_=False, args=None, env=None,
                interactive=False,self=None,
                replace=True):
        if env is None:
            env={}
        if self is None:
            self = MyEnv
        command  = Tools.text_strip(command, args=args, replace=replace)
        if "\n" in command:
            path = Tools._file_path_tmp_get()
            MyEnv.logger.debug("execbash:\n'''%s\n%s'''\n" % (path, command))
            command2 = ""
            if die:
                command2 = "set -ex\n"
            if cwd:
                command2 += "cd %s\n" % cwd
            command2+=command
            Tools.file_write(path, command2)
            command3 = "bash %s" % path
            res = Tools.execute(command3,showout=showout,useShell=useShell,cwd=cwd,
                            timeout=timeout,die=die,env=env,self=self)
            Tools.delete(path)
            return res
        else:


            if interactive:
                res = Tools._execute_interactive(cmd=command, die=die)
                logger.debug("execute interactive:%s"%command)
                Tools.shell()
            else:
                logger.debug("execute:%s"%command)

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
                            print(line, end="")

                    # Fold cache and return
                    return ''.join(data)

                else:
                    # This is not UNIX, most likely Win32. read() seems to work
                    def readout(stream):
                        line= stream.read().decode()
                        if showout:
                            # MyEnv.logger.debug(line)
                            print(line)


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

                        MyEnv.logger.warning("process killed because of timeout")
                        return (-2, out, err)

                    # Read out process streams, but don't block
                    out += readout(p.stdout)
                    err += readout(p.stderr)

            rc = -1 if p.returncode < 0 else p.returncode

            if rc<0 or rc>0:
                MyEnv.logger.debug('system.process.run ended, exitcode was %d' % rc)
            if out!="":
                MyEnv.logger.debug('system.process.run stdout:\n%s' % out)
            if err!="":
                MyEnv.logger.debug('system.process.run stderr:\n%s' % err)

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
    def cmd_installed(name):
        if not name in MyEnv._cmd_installed:
            MyEnv._cmd_installed[name] =  shutil.which(name) != None
        return MyEnv._cmd_installed[name]


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
        accountdir=os.path.join(MyEnv.config["DIR_BASE"],prefix,"github",account)
        repodir=os.path.join(MyEnv.config["DIR_BASE"],prefix,"github",account,repo)
        gitdir=os.path.join(MyEnv.config["DIR_BASE"],prefix,"github",account,repo,".git")
        dontpullloc=os.path.join(MyEnv.config["DIR_BASE"],prefix,"github",account,repo,".dontpull")
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

        url_ssh="git@github.com:%s/%s.git"%(account,repo)

        exists,foundgit,dontpull,ACCOUNT_DIR,REPO_DIR=Tools._code_location_get(account=account,repo=repo)

        args={}
        args["ACCOUNT_DIR"]= ACCOUNT_DIR
        args["REPO_DIR"]= REPO_DIR
        args["URL"] = url_ssh
        args["NAME"] = repo


        git_on_system = Tools.cmd_installed("git")


        if git_on_system and MyEnv.config["USEGIT"] and MyEnv.sshagent_active_check() and ((exists and foundgit) or not exists):
            #there is ssh-key loaded
            #or there is a dir with .git inside and exists
            #or it does not exist yet
            #then we need to use git

            C=""

            if exists==False:
                C="""
                set -ex
                mkdir -p {ACCOUNT_DIR}
                cd {ACCOUNT_DIR}
                git clone {URL}
                cd {NAME}
                """
            else:
                if Tools.code_changed(REPO_DIR):
                    if "GITMESSAGE" in os.environ:
                        args["MESSAGE"] = os.environ["GITMESSAGE"]
                    else:

                        args["MESSAGE"] = input("provide commit message python (or use env arg GITMESSAGE): ")
                    C="""
                    set -x
                    cd {REPO_DIR}
                    git add . -A
                    git commit -m "{MESSAGE}"
                    git pull

                    """

            Tools.log("get code [git]: %s"%repo)
            if C!="":
                Tools.execute(C, args=args)

            def getbranch(args):
                cmd = "cd {REPO_DIR}; git branch | grep \* | cut -d ' ' -f2"
                rc,stdout,err = Tools.execute(cmd, die=False, args=args, interactive=False)
                current_branch = stdout[1].strip()
                Tools.log("Found branch: %s" % current_branch)
                return current_branch

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
                val = [item.strip().strip("'").strip() for item in val2.split(",")]
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


class OSXInstall():

    @staticmethod
    def do_all():
        Tools.log("installing OSX version")
        UbuntuInstall.pips_install()


class UbuntuInstall():

    @staticmethod
    def do_all():
        Tools.log("installing Ubuntu version")

        UbuntuInstall.ensure_version()
        UbuntuInstall.change_apt_source()
        UbuntuInstall.ubuntu_base_install()
        UbuntuInstall.python_redis_install()
        UbuntuInstall.pips_install()

    @staticmethod
    def ensure_version():
        if not os.path.exists("/etc/lsb-release"):
            raise RuntimeError("Your operating system is not supported")

        with open("/etc/lsb-release", "r") as f:
            if "DISTRIB_CODENAME=bionic" not in f.read():
                raise RuntimeError("Your distribution is not supported. Only Ubuntu Bionic is supported.")

        return True

    @staticmethod
    def change_apt_source():
        if MyEnv.state_exists("change_apt_sources"):
            return

        script="""
        echo >> /etc/apt/sources.list
        echo "# Jumpscale Setup" >> /etc/apt/sources.list
        echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
        apt-get update
        """
        Tools.execute(script,interactive=True)
        MyEnv.state_set("change_apt_sources")

    @staticmethod
    def ubuntu_base_install():
        if MyEnv.state_exists("ubuntu_base_install"):
            return

        Tools.log("installing base system")

        script="""
        apt-get install -y python3-pip locales
        pip3 install ipython
        """
        Tools.execute(script, interactive=True)
        MyEnv.state_set("ubuntu_base_install")

    def python_redis_install():
        if MyEnv.state_exists("python_redis_install"):
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
    def pips_list(level=1):
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
                "certifi",
                "click>=6.6",
                "colored-traceback>=0.2.2",
                "colorlog>=2.10.0",
                # "credis",
                "cryptocompare",
                "cryptography>=2.2.0",
                "dnslib",
                "ed25519>=1.4",
                "fakeredis",
                "future>=0.15.0",
                "gevent >= 1.2.2",
                "gipc",
                "GitPython>=2.1.1",
                "grequests>=0.3.0",
                "httplib2>=0.9.2",
                "ipcalc>=1.99.0",
                "ipython<6.5.0>=6.0.0",
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
                "toml>=0.9.2",
                "Unidecode>=0.04.19",
                "watchdog>=0.8.3",
                "bpython",
                "pbkdf2"
            ],

            # level 1: in the middle
            1: [
                "zerotier>=1.1.2",
                "python-jose>=2.0.1",
                "itsdangerous>=0.24",
                "jsonschema>=2.5.1",
                "graphene>=2.0",
                "gevent-websocket",
                "Cython",
                "ovh>=0.4.7",
                "packet-python>=1.37",
                "uvloop>=0.8.0",
                "pycountry",
                "cson>=0.7",
                "ujson",
                "Pillow>=4.1.1",
            ],

            # level 2: full install
            2: [
                "psycopg2>=2.7.1",
                "pystache>=0.5.4",
                # "pypandoc>=1.3.3",
                "#SQLAlchemy>=1.1.9",
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

    def pips_install():
        for pip in UbuntuInstall.pips_list(0):

            if not MyEnv.state_exists("pip_%s"%pip):
                C="pip3 install '%s'"%pip
                Tools.execute(C,die=True)
                MyEnv.state_set("pip_%s"%pip)

    # def pip3(self):
    #     script="""
    #
    #     cd /tmp
    #     curl -sk https://bootstrap.pypa.io/get-pip.py > /tmp/get-pip.py || die "could not download pip" || return 1
    #     python3 /tmp/get-pip.py  >> ${LogFile} 2>&1 || die "pip install" || return 1
    #     rm -f /tmp/get-pip.py
    #     """
    #     Tools.execute(script,interactive=True)

class MyEnv():

    config = {}
    _sshagent_active = None
    sandbox_python_active = False
    sandbox_lua_active = False
    config_changed = False
    _cmd_installed = {}
    state = None
    _init = False
    FORMAT_LOG =  '{cyan!s}{asctime!s}{reset!s} - {filename:<18}:{name:12}-{lineno:4d}: {log_color!s}{levelname:<10}{reset!s} {message!s}'
    FORMAT_TIME = "%a%d %H:%M"

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
    def config_default_get():
        config = {}
        config["DIR_BASE"] = "/sandbox"
        config["DIR_TEMP"] = "/tmp/jumpscale"

        if "HOMEDIR" in os.environ:
            dir_home = os.environ["HOMEDIR"]
        elif "HOME" in os.environ:
            dir_home = os.environ["HOME"]
        else:
            dir_home = "/root"
        config["DIR_HOME"] = dir_home

        config["DIR_VAR"] = "/sandbox/var"
        config["DIR_CODE"] = "/sandbox/code"
        config["DIR_CFG"] = "/sandbox/cfg"
        config["USEGIT"] = True
        config["DEBUG"] = False
        config["SSH_AGENT"] = False

        config["LOGGER_ENABLE"] = True
        config["LOGGER_INCLUDE"] = []
        config["LOGGER_EXCLUDE"] = ["sal.fs"]
        config["LOGGER_LEVEL"] = 10

        if "INSYSTEM" in os.environ:
            if str(os.environ["INSYSTEM"]).lower().strip() in ["1","true","yes","y"]:
                config["INSYSTEM"] = True
            else:
                config["INSYSTEM"] = False
        else:
            if MyEnv.platform()=="linux":
                config["INSYSTEM"] = True
            else:
                config["INSYSTEM"] = True

        return config


    @staticmethod
    def init(force=False):

        if MyEnv._init:
            return

        if "DIR_CFG" in os.environ:
            DIR_CFG = os.environ["DIR_CFG"].strip()
        else:
            DIR_CFG = "/sandbox/cfg"

        MyEnv.config_file_path = os.path.join(DIR_CFG,"jumpscale_config.toml")
        MyEnv.state_file_path = os.path.join(DIR_CFG,"jumpscale_done.toml")

        if os.path.exists(MyEnv.config_file_path):
            MyEnv.config_load()
        else:
            MyEnv.config = MyEnv.config_default_get()
            MyEnv.config_save()

        if force or not MyEnv.state_exists("myenv_init"):

            if MyEnv.platform()== "linux":
                script="""
                echo >> /etc/apt/sources.list
                echo "# Jumpscale Setup" >> /etc/apt/sources.list
                echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
                apt-get update

                apt-get install -y curl rsync unzip
                locale-gen --purge en_US.UTF-8

                mkdir -p /tmp/jumpscale/scripts
                mkdir -p /sandbox/var/log

                """
            else:
                if not Tools.cmd_installed("curl") or Tools.cmd_installed("unzip") or Tools.cmd_installed("rsync"):
                    script="""
                    brew install curl unzip rsync
                    """
                else:
                    script = ""
                    Tools.error_raise("Cannot continue, curl, rsync, unzip needs to be installed")

            Tools.execute(script,interactive=True)


            MyEnv.config_load()

            if not "HOME" in MyEnv.config and "HOME" in os.environ:
                MyEnv.config["DIR_HOME"] = copy.copy(os.environ["HOME"])
                MyEnv.config_save()

            if not os.path.exists(MyEnv.config["DIR_BASE"]):
                script = """
                cd /
                sudo mkdir -p /sandbox/cfg
                sudo chown -R {USERNAME}:{GROUPNAME} /sandbox
                """
                args={}
                args["USERNAME"] = getpass.getuser()
                st = os.stat(MyEnv.config["DIR_HOME"])
                gid = st.st_gid
                args["GROUPNAME"] = grp.getgrgid(gid)[0]
                Tools.execute(script,interactive=True,args=args)


            installed = Tools.cmd_installed("git") and Tools.cmd_installed("ssh-agent")
            MyEnv.config["SSH_AGENT"]=installed
            MyEnv.config_save()

                # and
            if not os.path.exists(MyEnv.config["DIR_TEMP"]):
                os.makedirs(MyEnv.config["DIR_TEMP"],exist_ok=True)

            MyEnv.state_set("myenv_init")

        if os.path.exists(os.path.join(MyEnv.config["DIR_BASE"],"bin","python3.6")):
            MyEnv.sandbox_python_active=True
        else:
            MyEnv.sandbox_python_active=False

        MyEnv._init = True

    @staticmethod
    def install(force=False):
        #will get the sandbox installed
        if force or not MyEnv.state_exists("myenv_install"):

            if MyEnv.config["INSYSTEM"]:

                #DONT USE THE SANDBOX
                if MyEnv.platform() == "linux":
                    UbuntuInstall.do_all()
                else:
                    OSXInstall.do_all()

                Tools.code_github_get(repo="sandbox_base", branch=["master"])

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

            MyEnv.state_set("myenv_install")



    @staticmethod
    def sshagent_active_check():
        if MyEnv._sshagent_active is None:
            MyEnv._sshagent_active = len(Tools.execute("ssh-add -L",die=False,showout=False)[1])>40
        return MyEnv._sshagent_active
        # try:
        #     check_output(["pidof", "ssh-agent"])
        # except Exception as e:
        #     return False
        # return True

    @staticmethod
    def config_load():
        """
        only 1 level deep toml format only for int,string,bool
        no multiline
        """
        MyEnv.config = Tools.config_load(MyEnv.config_file_path)

    @staticmethod
    def config_save():
        Tools.config_save(MyEnv.config_file_path,MyEnv.config)

    @staticmethod
    def state_load():
        """
        only 1 level deep toml format only for int,string,bool
        no multiline
        """
        MyEnv.state = Tools.config_load(MyEnv.state_file_path,if_not_exist_create=True)

    @staticmethod
    def state_save():
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
    def state_exists(key):
        key = MyEnv._key_get(key)
        if MyEnv.state is None:
            MyEnv.state_load()
        if key in MyEnv.state:
            return True
        return False

    @staticmethod
    def state_set(key,val=True):
        key = MyEnv._key_get(key)
        if MyEnv.state is None:
            MyEnv.state_load()
        if key not in MyEnv.state or (key in MyEnv.state and MyEnv.state[key]!=val):
            MyEnv.state[key] = val
            MyEnv.state_save()



class JumpscaleInstaller():

    def __init__(self):

        MyEnv.install()

        self.account = "threefoldtech"
        self.branch = ["master"]

        Tools.file_touch(os.path.join(MyEnv.config["DIR_BASE"], "lib/jumpscale/__init__.py"))

        self._jumpscale_repos = [("jumpscaleX","Jumpscale"), ("digitalmeX","DigitalMe")]

        self.repos_get()
        self.repos_link()
        self.cmds_link()

        script="""
        set -e
        cd {DIR_BASE}
        source env.sh
        js_shell 'j.tools.console.echo("JumpscaleX IS OK.")'
        """
        Tools.execute(script,interactive=True)

    def repos_get(self,force=False):

        for sourceName,destName in self._jumpscale_repos:
            if MyEnv.sandbox_python_active:
                pull=True
            else:
                pull=False
            if force or not MyEnv.state_exists("jumpscale_repoget_%s"%sourceName):
                Tools.code_github_get(repo=sourceName, account=self.account, branch=self.branch, pull=pull)
                MyEnv.state_set("jumpscale_repoget_%s"%sourceName)

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
            Tools.log(Tools.text_strip("link {LOC}/{ALIAS} to {ALIAS}",args=args))
            Tools.execute(script,args=args)




    def cmds_link(self):

        exists,_,_,_,loc=Tools._code_location_get(repo="jumpscaleX",account=self.account)
        for src in os.listdir("%s/cmds" % loc):
            src2=os.path.join(loc,"cmds",src)
            dest="%s/bin/%s" % (MyEnv.config["DIR_BASE"], src)
            if not os.path.exists(dest):
                Tools.execute("ln -s {} {}".format(src2, dest))
                Tools.execute("chmod 770 {}".format(dest))
        Tools.execute("cd /sandbox;source env.sh;js_init generate")


formatter = LogFormatter()

logger = logging.Logger("installer")
logger.level = logging.INFO  #10 is debug

log_handler = logging.StreamHandler()
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

logging.basicConfig(level=logging.DEBUG)

MyEnv.logger = logger

MyEnv.init()

try:
    from colored_traceback import add_hook
    import colored_traceback
    add_hook()
    MyEnv._colored_traceback = colored_traceback
except ImportError:
    MyEnv._colored_traceback = None

try:
    import pygments
    import pygments.lexers
    MyEnv._lexer_python = pygments.lexers.Python3Lexer()
    #print(pygments.highlight(C,lexer, colored_traceback.Colorizer('default').formatter))
except ImportError:
    MyEnv._lexer_python = None
