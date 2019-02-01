from Jumpscale import j
import time
from watchdog.observers import Observer
from .MyFileSystemEventHandler import MyFileSystemEventHandler





class Syncer(j.application.JSBaseConfigClass):
    """
    make sure there is an ssh client first, can be done by

    j.clients.ssh.get...

    :param name:
    :param ssh_client_name: name as used in j.clients.ssh
    :param paths: specified as
        e.g.  "{DIR_CODE}/github/threefoldtech/0-robot:{DIR_TEMP}/0-robot,..."
        e.g.  "{DIR_CODE}/github/threefoldtech/0-robot,..."
        can use the {} arguments
        if destination not specified then is same as source

    if not specified is:
        paths = "{DIR_CODE}/github/threefoldtech/jumpscaleX,{DIR_CODE}/github/threefoldtech/digitalmeX"

    """
    _SCHEMATEXT = """
        @url = jumpscale.syncer.1
        name* = ""
        sshclient_name = ""
        paths = (LS)
        ignoredir = (LS)
        t = ""     
        """

    def _init(self,sshclient_name=None,ssh_client=None):

        if ssh_client:
            self.ssh_client = ssh_client
        elif sshclient_name:
            self.ssh_client = j.clients.ssh.get(name=self.sshclient_name)
        else:
            raise RuntimeError("need sshclient_name or ssh_client")

        self.IGNOREDIR = [".git", ".github"]
        self._executor = None

        # self.paths = []
        if self._isnew and self.paths==[]:
            self.paths.append("{DIR_CODE}/github/threefoldtech/jumpscaleX")
            self.paths.append("{DIR_CODE}/github/threefoldtech/digitalmeX")


    def delete(self):
        for item in j.clients.ssh.find(name=self.data.sshclient_name):
            item.delete()
        j.application.JSBaseConfigClass.delete(self)


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

            if not item.startswith("/") and not item.startswith("{") :
                item=j.sal.fs.getcwd()+"/"+item
            item = item.replace("//","/")

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
        print("WE ARE MONITORING")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
