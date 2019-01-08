import re
from io import StringIO
import os
import locale
from Jumpscale import j


class Profile(j.application.JSBaseClass):
    env_pattern = re.compile(r'([A-Za-z0-9_]+)=(.*)\n', re.MULTILINE)
    include_pattern = re.compile(r'(source|\.) (.*)$', re.MULTILINE)

    def __init__(self, bash, profilePath=None):
        """
        X="value"
        Y="value"
        PATH="p1:p2:p3"

        export X
        export Y
        """
        j.application.JSBaseClass.__init__(self)
        self.bash = bash
        self.executor = bash.executor
        self._pathProfile = profilePath or ""

        self.load()

    @property
    def pathProfile(self):
        if not self._pathProfile:
            self._pathProfile = j.sal.fs.joinPaths(
                self.home, ".profile_js")
        return self._pathProfile

    @pathProfile.setter
    def pathProfile(self, newpath):
        self._pathProfile = newpath

    def find_env_vars(self, content):
        """get defined environment variables in `content`
        this will match for XYZ=value

        :param content: content of e.g. a bash profile or the output of `printenv`
        :type content: str
        :return: a mapping between variables/values
        :rtype: dict
        """
        return dict(self.env_pattern.findall(content))

    def find_includes(self, content):
        """get included sources
        this will match for `source file.sh` or `. file.sh`

        :param content: content of e.g. bash profile
        :type content: str
        :return: a list of included files
        :rtype: list of str
        """
        return [match.group(2) for match in self.include_pattern.finditer(content)]

    def load(self):
        self.home = self.bash.home
        self._env = {}
        self._path = []
        self._includes = []

        # to let bash evaluate the profile source, we source the profile
        # then get the current environment variables using printenv
        content = self.executor.file_read(self.pathProfile)
        _, current_env, _ = self.executor.execute('source %s && printenv' % self.pathProfile)
        # get a set of profile variables and current environment variables
        profile_vars = self.find_env_vars(content).keys()
        current_env = self.find_env_vars(current_env)
        for var, value in current_env.items():
            if var in profile_vars:
                self._env[var] = value

        # includes
        self._includes.extend(self.find_includes(content))

        # load path
        if 'PATH' in self._env:
            path = self._env['PATH']
            _path = set(path.split(':'))
        else:
            _path = set()
        # make sure to add the js bin dir to the path
        if "SSHKEYNAME" not in self._env:
            self._env['sshkeyname'] = os.environ.get('SSHKEYNAME', 'id_rsa')

        _path.add(self.executor.replace("{DIR_BASE}/bin"))

        for item in _path:
            if item.strip() == "":
                continue
            if item.find("{PATH}") != -1:
                continue
            self.addPath(item)

        self._env.pop('PATH', None)

    def addPath(self, path):
        path = path.strip()
        path = path.replace("//", "/")
        path = path.replace("//", "/")
        path = path.rstrip("/")
        if path not in self._path:
            self._path.append(path)

    def addInclude(self, path):
        path = path.strip()
        path = path.replace("//", "/")
        path = path.replace("//", "/")
        path = path.rstrip("/")
        if path not in self._includes:
            self._includes.append(path)

    @property
    def paths(self):
        return list(self._path)

    def envSet(self, key, value):
        self._env[key] = value

    def envGet(self, key):
        return self._env[key]

    def envExists(self, key):
        return key in self._env

    def envDelete(self, key):
        del self._env[key]

    def envDeleteAll(self, key):
        """
        dangerous function will look for env argument
        which has been set in the profile
        if found will delete
        and will do this multiple times to make sure all instances are found
        """
        while self.envExists(key):
            self.envDelete(key)

    def deleteAll(self, key):
        while self.envExists(key):
            path = self.envGet(key)
            if path in self.paths:
                self._path.pop(self._path.index(path))
            self.envDelete(key)

    def pathDelete(self, filter):
        """
        @param filter e.g. /go/
        """
        for path in self.paths:
            if path.find(filter) != -1:
                self._path.pop(self._path.index(path))

    # def deletePathFromEnv(self, key):
    #     """
    #     dangerous function will look for env argument
    #       which has been set in the profile
    #     if found will delete
    #     and will do this multiple times to make sure all instances are found
    #     """
    #     while self.envExists(key):
    #         path = self.envGet(key)
    #         self.executor("rm -rf %s"%path)
    #         self.envDelete(key)

    def __str__(self):
        self._env['PATH'] = ':'.join(set(self.paths)) + ":${PATH}"

        content = StringIO()
        content.write('# environment variables\n')
        for key, value in self._env.items():
            content.write('%s="%s"\n' % (key, value))
            content.write('export %s\n\n' % key)

        content.write('# includes\n')
        for path in self._includes:
            if self.executor.exists(path):
                content.write('source %s\n' % path)

        self._env.pop('PATH')

        return content.getvalue()

    __repr__ = __str__

    @property
    def env(self):
        return self._env

    def replace(self, text):
        """
        will look for $ENVNAME 's and replace them in text
        """
        for key, val in self.env.items():
            text = text.replace("$%s" % key, val)
        return text

    def save(self, includeInDefaultProfile=True):
        """
        save to disk
        @param includeInDefaultProfile, if True then will
                include in the default profile
        """

        self.executor.file_write(self.pathProfile, str(self))

        # make sure we include our custom profile in the default
        if includeInDefaultProfile is True:
            if self.pathProfile != self.bash.profileDefault.pathProfile:
                self._logger.debug(
                    "INCLUDE IN DEFAULT PROFILE:%s" %
                    self.pathProfile)
                out = ""
                inProfile = self.executor.file_read(
                    self.bash.profileDefault.pathProfile)
                for line in inProfile.split("\n"):
                    if line.find(self.pathProfile) != -1:
                        continue
                    out += "%s\n" % line

                out += "\nsource %s\n" % self.pathProfile
                if out.replace("\n", "") != inProfile.replace("\n", ""):
                    self.executor.file_write(
                        self.bash.profileDefault.pathProfile, out)
                    self.bash.profileDefault.load()

        self.bash.reset()  # do not remove !

    def getLocaleItems(self, force=False, showout=False):

        if self.executor.type == "local":
            return [item for key, item in locale.locale_alias.items()]
        else:
            out = self.executor.execute("locale -a")[1]
            return out.split("\n")

    def locale_check(self):
        '''
        return true of locale is properly set
        '''
        if j.core.platformtype.myplatform.isMac:
            a = self.bash.env.get('LC_ALL') == 'en_US.UTF-8'
            b = self.bash.env.get('LANG') == 'en_US.UTF-8'
        else:
            a = self.bash.env.get('LC_ALL') == 'C.UTF-8'
            b = self.bash.env.get('LANG') == 'C.UTF-8'
        if (a and b) != True:
            self._logger.debug(
                "WARNING: locale has been fixed, please do: "
                "`source ~/.profile_js`")
            self.locale_fix()
            self.save(True)

    def locale_fix(self, reset=False):
        items = self.getLocaleItems()
        self.envSet("TERMINFO", "xterm-256colors")
        if "en_US.UTF-8" in items or "en_US.utf8" in items:
            self.envSet("LC_ALL", "en_US.UTF-8")
            self.envSet("LANG", "en_US.UTF-8")
            return
        elif "C.UTF-8" in items or "c.utf8" in items:
            self.envSet("LC_ALL", "C.UTF-8")
            self.envSet("LANG", "C.UTF-8")
            return
        raise j.exceptions.Input(
            "Cannot find C.UTF-8, cannot fix locale's")


class BashFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.tools.bash"

    def _init(self):
        self._local = None

    @property
    def local(self):
        if not self._local:
            self._local = Bash()
        return self._local

    def get(self, executor=None):
        """
        if executor==None then will be local
        """
        return Bash(executor=executor)


class Bash(object):

    def __init__(self, executor=None):
        self._executor = executor
        self._profile = None
        self.reset()

    @property
    def executor(self):
        if self._executor is None:
            self.executor = j.tools.executorLocal
        return self._executor

    @executor.setter
    def executor(self, newexecutor):
        self._executor = newexecutor

    def reset(self):
        self._profile = None
        self._profileDefault = None
        self.executor.reset()

    @property
    def env(self):
        dest = dict(self.profileJS.env)
        dest.update(self.executor.env)
        return dest

    @property
    def home(self):
        return self.executor.env.get("HOME") or self.executor.replace("{DIR_CODE}")

    def cmdGetPath(self, cmd, die=True):
        """
        checks cmd Exists and returns the path
        """
        rc, out, err = self.executor.execute(
            "source ~/.profile_js;which %s" % cmd, die=False, showout=False)
        if rc > 0:
            if die:
                raise j.exceptions.RuntimeError(
                    "Did not find command: %s" % cmd)
            else:
                return False

        out = out.strip()
        if out == "":
            raise RuntimeError("did not find cmd:%s" % cmd)

        return out

    def profileGet(self, path="~/.profile_js"):
        path = path.replace("~", self.home)
        if not self.executor.exists(path):
            self.executor.file_write(path, "")
        return Profile(self, path)

    @property
    def profileJS(self):
        """
        profile which we write for jumpscale std in ~/.profile_js
        """
        if self._profile is None:
            self._profile = self.profileGet()
        return self._profile

    @property
    def profileDefault(self):
        if self._profileDefault is None:
            path = "~/.bash_profile"
            self._profileDefault = self.profileGet(path)
        return self._profileDefault

    @property
    def profilePath(self):
        return self.profileDefault.pathProfile

    def locale_check(self):
        self.profileJS.locale_check()

    def locale_fix(self):
        self.profileJS.locale_fix()

    def envSet(self, key, val):
        self.profileJS.envSet(key, val)
        self.profileJS.save(True)

    def envGet(self, key):
        dest = dict(self.profileJS.env)
        dest.update(self.executor.env)
        return dest[key]

    def envDelete(self, key):
        if self.profileJS.envExists(key):
            self.profileJS.envDelete(key)
            self.profileJS.save(True) # issue #70
        else:
            del self.executor.env[key]
