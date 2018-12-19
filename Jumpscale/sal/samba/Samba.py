import signal
import sys
from io import StringIO

from Jumpscale import j
# from samba.netcmd.main import cmd_sambatool
from .sambaparser import SambaConfigParser

CONFIG_FILE = '/etc/samba/smb.conf'
EXCEPT_SHARES = ['global', 'printers', 'homes']
BASEPATH = '/VNASSHARE/'

JSBASE = j.application.JSBaseClass


class SMBUser(JSBASE):

    def __init__(self, verbose=False):
        JSBASE.__init__(self)
        # self._smb = cmd_sambatool(self._stdout, self._stderr)
        self._local = j.tools.executorLocal
        self._verbose = verbose

    def _smbrun(self, args):
        output = self._local.execute('samba-tool user %s ' % args)
        lines = output.splitlines()

        return lines

    def _format(self, output):
        if output[0].startswith("Warning:"):
            if self._verbose:
                self._logger.debug(output[0])

            return False

        return True

    def list(self):
        output = self._smbrun("list")
        return output

    def remove(self, username):
        output = self._smbrun("delete " + username)
        self._local.execute('userdel %s' % username)
        return self._format(output)

    def add(self, username, password):
        output = self._smbrun("add " + username + " " + password)
        self._local.execute("bash /etc/samba/update-uid.sh", True, False)
        self._local.execute('useradd %s' % username)
        return self._format(output)

    def grantaccess(self, username, sharename, sharepath, readonly=True):
        sharepath = j.tools.path.get(BASEPATH).joinpath(sharepath, sharename)
        if not sharepath.exists():
            return False
        group = '%s%s' % (sharename, 'r' if readonly else 'rw')
        self._local.execute('usermod -a %s %s' % (group, username))
        return True

    def revokeaccess(self, username, sharename, sharepath, readonly=True):
        sharepath = j.tools.path.get(BASEPATH).joinpath(sharepath, sharename)
        if sharepath.exists():
            group = '%s%s' % (sharename, 'r' if readonly else 'rw')
            self._local.execute('deluser %s %s' % (username, group))
        return True


class SMBShare(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)
        self._config = SambaConfigParser()
        self._load()

    def _load(self):
        config = j.tools.path.get(CONFIG_FILE)
        if not config.exists():
            config.parent.mkdir_p()
            config.touch()
        cfg = config.text()
        data = StringIO('\n'.join(line.strip() for line in cfg.splitlines()))
        self._config.readfp(data)

    def get(self, sharename):
        # special share which we don't handle
        if sharename in EXCEPT_SHARES:
            return False

        # share name not found
        if not self._config.has_section(sharename):
            return False

        return self._config.items(sharename)

    def remove(self, sharename):
        # don't touch special shares (global, ...)
        if sharename in EXCEPT_SHARES:
            return False

        if not self._config.has_section(sharename):
            return False

        self._config.remove_section(sharename)
        return True

    def add(self, sharename, path, options={}):
        # share already exists or is denied
        if self._config.has_section(sharename):
            return False

        if sharename in EXCEPT_SHARES:
            return False

        # set default options
        self._config.add_section(sharename)
        self._config.set(sharename, 'path', path)

        # set user defined options
        for option in options:
            self._config.set(sharename, option, options[option])

        return True

    def commit(self):
        sio = StringIO()
        self._config.write(sio)
        config = j.tools.path.get(CONFIG_FILE)
        config.write_text(sio.getvalue())

        # reload config
        j.sal.process.killProcessByName('smbd', signal.SIGHUP)
        j.sal.process.killProcessByName('nmbd', signal.SIGHUP)

        return True

    def list(self):
        shares = self._config.sections()
        result = dict()
        for sharename in shares:
            if sharename in EXCEPT_SHARES:
                # special share which we don't handle
                continue
            shareinfo = self._config.items(sharename)
            result[sharename] = {info[0]: info[1] for info in shareinfo}

        return result


class SMBSubShare(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)
        j.tools.path.get(BASEPATH).mkdir_p()
        self._local = j.tools.executorLocal

    def get(self, sharename, sharepath):
        sharepath = j.tools.path.get(BASEPATH).joinpath(sharepath, sharename)
        if not sharepath.exists():
            return False

        acls = dict()
        for access in ['r', 'rw']:
            groupname = '%s%s' % (sharename, access)
            groupinfo = self._local.execute('getent group %s' % groupname)
            users = groupinfo.split(':')[-1] if groupinfo else ''
            users = users.split(',') if users else []
            acls[access] = users

        return {sharename: acls}

    def remove(self, sharename, sharepath):
        sharepath = j.tools.path.get(BASEPATH).joinpath(sharepath, sharename)
        sharepath.rmtree_p()
        for access in ['r', 'rw']:
            self._local.execute('groupdel %s%s' % (sharename, access))
        return True

    def add(self, sharename, sharepath):
        # Create dir under BASEPATH
        # Create two groups for access: one readonly and one rw
        sharepath = j.tools.path.get(BASEPATH).joinpath(sharepath, sharename)
        sharepath.mkdir_p()

        for access in ['r', 'rw']:
            groupname = '%s%s' % (sharename, access)
            self._local.execute('groupadd %s' % groupname)
            self._local.execute(
                'setfacl -m g:%s:%s %s' %
                (groupname, access, sharepath))

        return True

    def list(self, path=''):
        sharepath = j.tools.path.get(BASEPATH).joinpath(path)
        subshares = self._local.execute(
            r'find %s -maxdepth 1 -type d -exec basename {} \;' %
            sharepath).splitlines()
        result = list()
        for subshare in subshares:
            if subshare == j.tools.path.get(path.rstrip('/')).basename():
                continue
            result.append(self.get(subshare, sharepath))
        return result


class Samba(JSBASE):

    __jslocation__ = "j.sal.samba"

    def __init__(self):
        JSBASE.__init__(self)
        self._local = j.tools.executorLocal
        self._users = SMBUser(True)
        self._shares = SMBShare()
        self._subshares = SMBSubShare()

    def getShare(self, sharename):
        return self._shares.get(sharename)

    def listShares(self):
        return self._shares.list()

    def removeShare(self, sharename):
        return self._shares.remove(sharename)

    def addShare(self, sharename, path, options={}):
        return self._shares.add(sharename, path, options)

    def commitShare(self):
        return self._shares.commit()

    def getSubShare(self, sharename, sharepath):
        return self._subshares.get(sharename)

    def removeSubShare(self, sharename, sharepath):
        return self._subshares.remove(sharename, sharepath)

    def addSubShare(self, sharename, sharepath):
        return self._subshares.add(sharename, sharepath)

    def listSubShares(self, path):
        return self._subshares.list(path)

    def listUsers(self):
        return self._users.list()

    def removeUser(self, username):
        return self._users.remove(username)

    def addUser(self, username, password):
        return self._users.add(username, password)

    def grantaccess(self, username, sharename, sharepath, readonly=True):
        return self._users.grantaccess(
            username, sharename, sharepath, readonly)

    def revokeaccess(self, username, sharename, sharepath, readonly=True):
        return self._users.revokeaccess(
            username, sharename, sharepath, readonly)


# class SambaFactory:

#     def _getFactoryEnabledClasses(self):
#         return (("", "Samba", Samba()), ("Samba", "SMBUser", SMBUser()), ("Samba", "SMBShare", SMBShare()),
#                 ("Samba", "SMBSubShare", SMBSubShare()), ("Samba", "SambaConfigParser", SambaConfigParser()))

#     def get(self, con):
#         return Samba()
