from Jumpscale import j

import os
import re


# EXPORTS_FILE = j.tools.path.get('/etc/exports')

EXPORT_OPT_REGEXT = re.compile('^(?:([\w/]+)|"([\w\s/]+)")\s+(.+)$')
CLIENT_OPT_REGEXT = re.compile('\s*([^\(]+)\(([^\)]+)\)')
JSBASE = j.application.JSBaseClass

class NFSError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class NFSExport(j.application.JSBaseClass):

    def __init__(self, path=""):
        self.__jslocation__ = "j.sal.nfs"
        JSBASE.__init__(self)
        self._path = j.tools.path.get(path)
        self._clients = []

    @property
    def path(self):
        return self._path

    @property
    def clients(self):
        return self._clients

    def addClient(self, name='*', options='rw,sync'):
        name = name.replace(' ', '')
        options = options.replace(' ', '')

        self._clients.append((name, options))

    def removeClient(self, name):
        name = name.replace(' ', '')
        for i in range(len(self._clients) - 1, -1, -1):
            if self._clients[i][0] == name:
                self._clients.pop(i)

    def __str__(self):
        buf = list()
        buf.append('"%s"' % self._path)
        for client in self._clients:
            buf.append(' %s(%s)' % client)

        return ''.join(buf)

    def __repr__(self):
        return str(self)


class NFS(j.application.JSBaseClass):

    def __init__(self):
        self._exports = None
        self._executor = j.tools.executorLocal
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
        if self._exports is None:
            self._load()
        return self._exports

    def add(self, path):
        export = NFSExport(path)
        self.exports.append(export)
        return export

    def delete(self, path):
        for i in range(len(self.exports) - 1, -1, -1):
            export = self.exports[i]
            if export.path == path:
                self.exports.pop(i)

    def erase(self):
        self._exports = []

    def commit(self):
        buf = list()
        for export in self.exports:
            buf.append(export.__str__())

        EXPORTS_FILE.write_text("\n".join(buf))
        EXPORTS_FILE.chmod(644)
        try:
            self._executor.execute('service nfs-kernel-server reload')
        except Exception as e:
            raise NFSError(e)
