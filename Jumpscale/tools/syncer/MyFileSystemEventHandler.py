from Jumpscale import j
JSBASE = j.application.JSBaseClass


from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class MyFileSystemEventHandler(FileSystemEventHandler, JSBASE):
    def __init__(self,paths,zoscontainer):
        JSBASE.__init__(self)
        self.zoscontainer = zoscontainer
        self.paths = paths
        self._logger_enable()
        self.sync_paths_src=[]
        self.sync_paths_dest=[]
        for source in self.paths:
            if not j.data.types.list.check(source):
                dest=source
            else:
                source,dest=source #get list to 2 separate ones
            if ":" in source:
                raise RuntimeError("cannot have : in source")
            self.sync_paths_src.append(j.tools.prefab.local.core.replace(source))
            self.sync_paths_dest.append(j.tools.prefab.local.core.replace(dest))
            #THERE IS ISSUE WITH PATHS when not sandbox
            # self.sync_paths_dest.append(self.zoscontainer.node.prefab.core.replace(dest))

    def path_dest_get(self,src):
        nr=0
        for item in self.sync_paths_src:
            dest = self.sync_paths_dest[nr]
            if src.startswith(item):
                dest = j.sal.fs.joinPaths(dest,j.sal.fs.pathRemoveDirPart(src,item))
                return dest
            nr+=1
        raise RuntimeError("did not find:%s"%src)

    def handler(self, event, action="copy"):
        self._logger.debug("%s:%s" % (event, action))
        changedfile = event.src_path
        if event.is_directory:
            if changedfile.find("/.git") != -1:
                return
            elif changedfile.find("/__pycache__/") != -1:
                return
            elif changedfile.find(".egg-info") != -1:
                return
            if event.event_type == "modified":
                return
            self.zoscontainer.sync(paths=self.zoscontainer.sync_paths,monitor=False)
        else:

            error = False
            node = self.zoscontainer.node
            if error is False:
                if changedfile.find("/.git") != -1:
                    return
                elif changedfile.find("/__pycache__/") != -1:
                    return
                elif changedfile.endswith(".pyc"):
                    return
                dest = self.path_dest_get(changedfile)
                e = ""

                if action == "copy":
                    self._logger.debug("copy: %s %s:%s" % (changedfile, node, dest))
                    try:
                        node.sftp.put(changedfile, dest)
                    except Exception as e:
                        self._logger.debug("** ERROR IN COPY, WILL SYNC ALL")
                        self._logger.debug(str(e))
                        error = True
                elif action == "delete":
                    self._logger.debug("delete: %s %s:%s" % (changedfile, node, dest))
                    try:
                        node.sftp.remove(dest)
                    except Exception as e:
                        if "No such file" in str(e):
                            return
                        else:
                            error = True
                            # raise RuntimeError(e)
                else:
                    raise j.exceptions.RuntimeError(
                        "action not understood in filesystemhandler on sync:%s" % action)

                if error:
                    try:
                        self._logger.debug(e)
                    except BaseException:
                        pass
                    node.sync()
                    error = False

    def on_moved(self, event):
        j.tools.develop.sync()
        self.handler(event, action="delete")

    def on_created(self, event):
        self.handler(event)

    def on_deleted(self, event):
        self.handler(event, action="delete")

    def on_modified(self, event):
        self.handler(event)
