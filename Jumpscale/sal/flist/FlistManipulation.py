from Jumpscale import j


class FlistManipulation(j.application.JSBaseClass):
    """
    this sal using zflist bin should install using `j.builders.storage.zflist.install(reset=True)`
    """

    __jslocation__ = "j.sal.flist"

    def __init__(self):
        self.temporary_point = "/tmp"
        self.hub_host = "playground.hub.grid.tf"
        self.port = 9910

    def _prefix(self):
        cmd = """
        export ZFLIST_BACKEND='{"host": "%s", "port": %s}'
        export ZFLIST_MNT="%s"
        
        """ % (
            self.hub_host,
            self.port,
            self.temporary_point,
        )
        return cmd

    def new_flist(self):
        """
        initialize an empty flist to enable editing
        """
        cmd = """
        zflist init 
        """
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def open_flist(self, path):
        """
        open an flist to enable editing
        """
        cmd = """
        zflist open {} 
        """.format(
            path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def file_copy_from_local(self, path, dest):
        """
        insert local file into the flist
        """
        cmd = """
        zflist put {path} {dest}
        """.format(
            path=path, dest=dest
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def dir_copy_from_local(self, path, dest):
        """
        insert local directory into the flist (recursively)
        """
        cmd = """
        zflist putdir {path} {dest}
        """.format(
            path=path, dest=dest
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def remove_file(self, path):
        """
        remove a file (not a directory)
        """
        cmd = """
        zflist rm {path}
        """.format(
            path=path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def remove_dir(self, path):
        """
        remove a directory (recursively)
        """
        cmd = """
        zflist rmdir {path}
        """.format(
            path=path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def create_dir(self, path):
        """
        create an empty directory (non-recursive)
        """
        cmd = """
        zflist mkdir {path}
        """.format(
            path=path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def merge(self, flist_path):
        """
        merge another flist into the current one
        """
        cmd = """
        zflist merge {path}
        """.format(
            path=flist_path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def chmod_file(self, reference, operator, mode, file_path):
        """
        change mode of a file (like chmod command)
        chmod [reference][operator][mode] file... 
        """
        cmd = """
        zflist chmod {}{}{} {}
        """.format(
            reference, operator, mode, file_path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def list_content(self, path="/"):
        """
       list the content of a directory in flist
        """
        cmd = """
        zflist ls {path}
        """.format(
            path=path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def list_all(self):
        """
       list full contents of files and directories
        """
        cmd = """
        zflist find
        """
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def set_metadata(self, hub_host="playground.hub.grid.tf", port=9910):
        """
       set metadata
        """
        cmd = """
        zflist metadata backend --host {} --port {}
        """.format(
            hub_host, port
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def print_content(self, path):
        """
        print file contents (backend metadata required)
        """
        self.set_metadata()
        cmd = """
        zflist cat {}
        """.format(
            path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def commit(self, path="/tmp/zflist_sal.flist"):
        """
        commit changes to a new flist
        """
        self.set_metadata()
        cmd = """
        zflist commit {}
        """.format(
            path
        )
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

    def close(self):
        """
        close mountpoint and discard files
        """
        self.set_metadata()
        cmd = """
        zflist close
        """
        newcmd = self._prefix() + cmd
        j.sal.process.execute(newcmd)

