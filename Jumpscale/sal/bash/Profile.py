from Jumpscale import j
import re
import os
from io import StringIO
import locale

class Profile(j.application.JSBaseClass):
    _env_pattern = re.compile(r'([A-Za-z0-9_]+)=(.*)\n', re.MULTILINE)
    _include_pattern = re.compile(r'(source|\.) (.*)$', re.MULTILINE)

    def __init__(self, bash, profile_path=None):
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
        if profile_path:
            self.profile_path = profile_path
        else:
            self.profile_path = j.sal.fs.joinPaths(self.home, ".profile_js")

        self.load()


    def _env_vars_find(self, content):
        """get defined environment variables in `content`
        this will match for XYZ=value

        :param content: content of e.g. a bash profile or the output of `printenv`
        :type content: str
        :return: a mapping between variables/values
        :rtype: dict
        """
        return dict(self._env_pattern.findall(content))

    def _includes_find(self, content):
        """get included sources
        this will match for `source file.sh` or `. file.sh`

        :param content: content of e.g. bash profile
        :type content: str
        :return: a list of included files
        :rtype: list of str
        """
        return [match.group(2) for match in self._include_pattern.finditer(content)]

    def load(self):

        if self.profile_path.startswith("/sandbox"):
            self.is_sandbox = True
        else:
            self.is_sandbox = False

        if self.is_sandbox:
            self.home = "/sandbox"
        else:
            self.home = self.bash.home

        self._env = {}
        self._path = []
        self._includes = []

        if not self.executor.exists(self.profile_path):
            self.executor.file_write(self.profile_path,"")

        # to let bash evaluate the profile source, we source the profile
        # then get the current environment variables using printenv
        content = self.executor.file_read(self.profile_path)
        if self.is_sandbox:
            _, current_env, _ = self.executor.execute('source /sandbox/env.sh;printenv')
        else:
            _, current_env, _ = self.executor.execute('source %s && printenv' % self.profile_path)

        # get a set of profile variables and current environment variables
        profile_vars = self._env_vars_find(content).keys()
        current_env = self._env_vars_find(current_env)
        for var, value in current_env.items():
            if var in profile_vars:
                self._env[var] = value

        # includes
        self._includes.extend(self._includes_find(content))

        # load path
        if 'PATH' in self._env:
            path = self._env['PATH']
            _path = set(path.split(':'))
        else:
            _path = set()

        # make sure to add the js bin dir to the path
        # if "SSHKEYNAME" not in self._env:
        #     self._env['sshkeyname'] = os.environ.get('SSHKEYNAME', 'id_rsa')

        _path.add(self.executor.replace("{DIR_BASE}/bin"))

        for item in _path:
            if item.strip() == "":
                continue
            if item.find("{PATH}") != -1:
                continue
            self.path_add(item)

        self._env.pop('PATH', None)

    def path_add(self, path):
        """

        :param path:
        :return:
        """
        path = path.strip()
        path = path.replace("//", "/")
        path = path.replace("//", "/")
        path = path.rstrip("/")
        if path not in self._path:
            self._path.append(path)

    def include_add(self, path):
        path = path.strip()
        path = path.replace("//", "/")
        path = path.replace("//", "/")
        path = path.rstrip("/")
        if path not in self._includes:
            self._includes.append(path)

    @property
    def paths(self):
        return list(self._path)

    def env_set(self, key, value):
        self._env[key] = value

    def env_get(self, key):
        return self._env[key]

    def env_exists(self, key):
        return key in self._env

    def env_delete(self, key):
        if self.env_exists(key):
            del self._env[key]

    def reset(self, key):
        while self.env_exists(key):
            path = self.env_get(key)
            if path in self.paths:
                self._path.pop(self._path.index(path))
            self.env_delete(key)

    def path_delete(self, filter):
        """
        @param filter e.g. /go/
        """
        for path in self.paths:
            if path.find(filter) != -1:
                self._path.pop(self._path.index(path))


    def __str__(self):
        self._env['PATH'] = ':'.join(set(self.paths)) + ":${PATH}"

        content = StringIO()
        content.write('# environment variables\n')
        for key, value in self._env.items():
            content.write('export %s="%s"\n' % (key, value))

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

    def save(self, includeInDefaultProfile=False):
        """
        save to disk
        @param includeInDefaultProfile, if True then will
                include in the default profile
        """

        self.executor.file_write(self.profile_path, str(self))

        # make sure we include our custom profile in the default
        if includeInDefaultProfile is True:
            if self.profile_path != self.bash.profile.profile_path:
                self._log_debug("INCLUDE IN DEFAULT PROFILE:%s" %self.profile_path)
                out = ""
                inProfile = self.executor.file_read(
                    self.bash.profile_default.profile_path)
                for line in inProfile.split("\n"):
                    if line.find(self.profile_path) != -1:
                        continue
                    out += "%s\n" % line

                out += "\nsource %s\n" % self.profile_path
                if out.replace("\n", "") != inProfile.replace("\n", ""):
                    self.executor.file_write(
                        self.bash.profile_default.profile_path, out)
                    self.bash.profile_default.load()

        self.bash.reset()  # do not remove !

    def locale_items_get(self, force=False, showout=False):

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
            self._log_debug(
                "WARNING: locale has been fixed, please do: "
                "`source ~/.profile_js`")
            self.locale_fix()
            self.save(True)

    def locale_fix(self, reset=False):
        items = self.locale_items_get()
        self.env_set("TERMINFO", "xterm-256colors")
        if "en_US.UTF-8" in items or "en_US.utf8" in items:
            self.env_set("LC_ALL", "en_US.UTF-8")
            self.env_set("LANG", "en_US.UTF-8")
            return
        elif "C.UTF-8" in items or "c.utf8" in items:
            self.env_set("LC_ALL", "C.UTF-8")
            self.env_set("LANG", "C.UTF-8")
            return
        raise j.exceptions.Input(
            "Cannot find C.UTF-8, cannot fix locale's")
