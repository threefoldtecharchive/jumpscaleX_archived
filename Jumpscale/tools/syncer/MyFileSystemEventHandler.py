from Jumpscale import j

JSBASE = j.application.JSBaseClass


from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class MyFileSystemEventHandler(FileSystemEventHandler, JSBASE):
    def __init__(self, syncer):
        JSBASE.__init__(self)
        self.syncer = syncer
        self.paths = syncer.paths

        self.sync_paths_src = []
        self.sync_paths_dest = []
        for source in self.syncer._get_paths():
            if not j.data.types.list.check(source):
                dest = source
            else:
                source, dest = source  # get list to 2 separate ones
            if ":" in source:
                raise RuntimeError("cannot have : in source")
            self.sync_paths_src.append(j.builders.tools.replace(source))
            self.sync_paths_dest.append(j.builders.tools.replace(dest))
        self._logger_enable()

    def path_dest_get(self, src):
        nr = 0
        for item in self.sync_paths_src:
            dest = self.sync_paths_dest[nr]
            if src.startswith(item):
                dest = j.sal.fs.joinPaths(dest, j.sal.fs.pathRemoveDirPart(src, item))
                return dest
            nr += 1
        raise RuntimeError("did not find:%s" % src)

    def handler(self, event, action="copy"):
        # self._log_debug("%s:%s" % (event, action))
        ftp = self.syncer.ssh_client.sftp
        changedfile = event.src_path
        if event.src_path.endswith((".swp", ".swx")):
            return
        elif event.is_directory:
            if changedfile.find("/.git") != -1:
                return
            elif changedfile.find("/__pycache__/") != -1:
                return
            elif changedfile.find(".egg-info") != -1:
                return
            if event.event_type == "modified":
                return
            self.syncer.sync(monitor=False)
        else:

            error = False

            if error is False:
                print(changedfile)
                if changedfile.find("/.git") != -1:
                    return
                elif changedfile.find("/__pycache__/") != -1:
                    return
                elif changedfile.find("/_tmp_/") != -1:
                    return
                elif changedfile.endswith(".pyc"):
                    return
                elif changedfile.endswith("___"):
                    return
                dest = self.path_dest_get(changedfile)
                e = ""

                if action == "copy":
                    self._log_debug("copy: %s:%s" % (changedfile, dest))
                    print("copy: %s:%s" % (changedfile, dest))
                    try:
                        self.syncer.ssh_client.copy_file(changedfile, dest)
                    except Exception as e:
                        self._log_error("Couldn't sync file: %s:%s" % (changedfile, dest))
                        self._log_error("** ERROR IN COPY, WILL SYNC ALL")
                        self._log_error(str(e))
                        error = True
                elif action == "delete":
                    self._log_debug("delete: %s:%s" % (changedfile, dest))
                    try:
                        cmd = "rm %s" % dest
                        self.syncer.ssh_client.exec_command(cmd)
                    except Exception as e:
                        self._log_error("Couldn't remove file: %s" % (dest))
                        if "No such file" in str(e):
                            return
                        else:
                            error = True
                            # raise RuntimeError(e)
                else:
                    raise j.exceptions.RuntimeError("action not understood in filesystemhandler on sync:%s" % action)

                if error:
                    try:
                        self._log_debug(e)
                    except BaseException:
                        pass
                    self.syncer.sync(monitor=False)
                    error = False

    def on_moved(self, event):
        self.syncer.sync(monitor=False)
        self.handler(event, action="delete")

    def on_created(self, event):
        self.handler(event)

    def on_deleted(self, event):
        self.handler(event, action="delete")

    def on_modified(self, event):
        self.handler(event)
