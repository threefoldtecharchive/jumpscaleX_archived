from Jumpscale import j
from subprocess import run, PIPE
import os
import re


EXPORTS_FILE = j.tools.path.get('/etc/exports')

EXPORT_OPT_REGEXT = re.compile('^(?:([\w/]+)|"([\w\s/]+)")\s+(.+)$')
CLIENT_OPT_REGEXT = re.compile('\s*([^\(]+)\(([^\)]+)\)')
JSBASE = j.application.JSBaseClass

class NFSError(Exception):
    def __init__(self, message=""):
        super().__init__(message)


class NFSExport(JSBASE):
    def __init__(self, path=""):
        JSBASE.__init__(self)
        self._path = j.tools.path.get(path)
        self._clients = []

    @property
    def path(self):
        """
        shared directory path 
        """
        return self._path

    @property
    def clients(self):
        """
        list clients and their permissions for the shared directory
        """
        return self._clients

    def addClient(self, name='*', options='rw,sync'):
        """
        add client on the same network to access shared directory
        @param name: can be hostname,
                            ip address (ex: 192.168.0.4),
                            ip networks (ex: 192.168.0.1/24)
                            wildcards (ex: *)
                     type: string
        @param options: client premissions
                        can be ro (read only)
                               rw (read/write)
                               sync (sync writing back to the disk)
                               no_subtree_check (no checking if the requested file from the client is in the appropriate part of the volume)
                               no_root_squash (root on the client machine will have the same level of access to the files on the system as root on the server)
                        type: string (for multiple options "rw,sync")
        """
        for client in self.clients:
            if client[0] == name:
                raise NFSError("client {} is already added".format(name))

        name = name.replace(' ', '')
        options = options.replace(' ', '')

        self._clients.append((name, options))

    def removeClient(self, name):
        """
        remove client from accessing shared directory
        @param name: hostname
                     type: string
        """
        name = name.replace(' ', '')
        for i in range(len(self._clients) - 1, -1, -1):
            if self._clients[i][0] == name:
                self._clients.pop(i)
                break
        else:
            raise NFSError("Client {} is not found".format(name))

    def __str__(self):
        buf = list()
        buf.append('"%s"' % self._path)
        for client in self._clients:
            buf.append(' %s(%s)' % client)

        return ''.join(buf)

    def __repr__(self):
        return str(self)


class NFS(JSBASE):
    def __init__(self):
        self._exports = None
        self.__jslocation__ = "j.sal.nfs"
        JSBASE.__init__(self)

    def _load(self):
        exports = []
        try:
            content = EXPORTS_FILE.text()
            lineparts = []
            for linepart in content.split(os.linesep):
                linepart = linepart.strip()
                if linepart == '' or linepart.startswith('#'):
                    continue

                lineparts.append(linepart)

                if linepart.endswith('\\'):
                    lineparts.append(linepart)
                    continue

                line = ' '.join(lineparts)
                lineparts = []

                match = EXPORT_OPT_REGEXT.match(line)
                if not match:
                    raise NFSError("Invalid line '%s'" % line)

                path = match.group(1) or match.group(2)
                export = NFSExport(path)
                exports.append(export)

                opts = match.group(3)
                for clientm in re.finditer(CLIENT_OPT_REGEXT, opts):
                    export.addClient(clientm.group(1), clientm.group(2))
        except Exception as e:
            raise NFSError(e)

        self._exports = exports

    @property
    def exports(self):
        """
        list shared directories
        """
        if self._exports is None:
            self._load()
        return self._exports

    def add(self, path):
        """
        add shared directory
        @param path: directory path
                     type: string
        """
        for export in self.exports:
            if export.path == path:
                raise NFSError("Path {} is already added".format(path))

        export = NFSExport(path)
        self.exports.append(export)
        return export

    def delete(self, path):
        """
        delete path from shared directories
        @param path: directory path
                     type: string
        """
        for i in range(len(self.exports) - 1, -1, -1):
            export = self.exports[i]
            if export.path == path:
                self.exports.pop(i)
                break
        else:
            raise NFSError("Path {} is not found".format(path))

    def erase(self):
        """
        delete all shared directories
        """
        self._exports = []

    def commit(self):
        """
        apply changes to shared directories
        """
        buf = list()
        for export in self.exports:
            buf.append(export.__str__())

        EXPORTS_FILE.write_text("\n".join(buf))
        EXPORTS_FILE.chmod(644)
        response = run('service nfs-kernel-server reload', shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
        if response.stderr:
            raise NFSError(response.stderr.strip())
        return response.stdout.strip()