from Jumpscale import j
import time
from watchdog.observers import Observer
from .MyFileSystemEventHandler import MyFileSystemEventHandler


class Syncer(j.application.JSBaseConfigClass):
    _SCHEMATEXT = """
        @url = jumpscale.syncer.1
        name* = ""
        sshclient_name = ""
        paths = (LS)
        ignoredir = (LS)        
        """

    def _init(self):

        j.application.JSBaseConfigClass._init(self)

        self.ssh_client = j.clients.ssh.get(name=self.sshclient_name)

        self.IGNOREDIR = [".git", ".github"]
        self._executor = None


    def data_update(self,**kwargs):
        if "paths" in kwargs:
            paths = kwargs["paths"]
            if not j.data.types.list.check(paths):
                paths2=[]
                for item in paths.split(","):
                    item=item.strip()
                    if not item.startswith("/") and not item.startswith("{") :
                        item=j.sal.fs.getcwd()+"/"+item
                    item = item.replace("//","/")
                    paths2.append(item)
                kwargs["paths"]=paths2
        self.data.load_from_data(data=kwargs,reset=False)
        self.data.save()

    @property
    def executor(self):
        if not self._executor:
            self._executor = j.tools.executor.ssh_get(self.ssh_client)
        return self._executor

    def _get_paths(self):
        """

        :return: [[src,dest],...]
        """
        res=[]
        for item in self.paths:
            items = item.split(":")
            if len(items)==1:
                src = items[0]
                dst = src
            elif len(items)==2:
                src = items[0]
                dst = items[1]
            else:
                raise RuntimeError("can only have 2 parts")
            src= j.core.tools.text_replace(src)
            if "{" in dst:
                dst = self.executor.replace(dst)
            res.append((src,dst))
        return res

    def sync(self, monitor=True):
        """
        sync all code to the remote destinations, uses config as set in jumpscale.toml

        paths is [path1, path2,...] or [["/src",'/dest'],["/src2",'/dest2']]

        can use {} (the dir paths in the dir's


        """

        for item in self._get_paths():
            source,dest = item
            self._logger.info("upload:%s to %s"%(source,dest))
            self.executor.upload(source, dest, recursive=True, createdir=True,
                                 rsyncdelete=True, ignoredir=self.IGNOREDIR, ignorefiles=None)

        if monitor:
            self._monitor()

    def _monitor(self):
        """
        look for changes in directories which are being pushed & if found push to remote nodes

        paths is [path1, path2,...] or [["/src",'/dest'],["/src2",'/dest2']]

        js_shell 'j.tools.develop.monitor()'

        """

        event_handler = MyFileSystemEventHandler( syncer=self)
        observer = Observer()
        for item in self._get_paths():
            source,dest = item
            self._logger.info("monitor:%s" % source)
            observer.schedule(event_handler, source, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
