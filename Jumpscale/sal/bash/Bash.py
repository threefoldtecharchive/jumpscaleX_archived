from Jumpscale import j
from .Profile import  Profile

class Bash(object):

    def __init__(self, executor=None,profile_path=None):
        self._executor = executor
        self._profile = None
        self.profile = Profile(self,profile_path)
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
        self._profile_default = None
        self.executor.reset()

    @property
    def env(self):
        dest = dict(self.profile.env)
        dest.update(self.executor.env)
        return dest

    @property
    def home(self):
        return self.executor.env.get("HOME") or self.executor.replace("{DIR_CODE}")

    def cmd_path_get(self, cmd, die=True):
        """
        checks cmd Exists and returns the path
        """
        rc, out, err = self.executor.execute("source %s;which %s" % (self.profile.path,cmd), die=False, showout=False)
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

    def locale_check(self):
        self.profile.locale_check()

    def locale_fix(self):
        self.profile.locale_fix()

    def env_set(self, key, val):
        self.profile.env_set(key, val)
        self.profile.save(True)

    def env_get(self, key):
        dest = dict(self.profile.env)
        dest.update(self.executor.env)
        return dest[key]

    def env_delete(self, key):
        if self.profile.env_exists(key):
            self.profile.env_delete(key)
            self.profile.save(True) # issue #70
        else:
            del self.executor.env[key]
