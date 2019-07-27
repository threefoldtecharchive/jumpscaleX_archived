from Jumpscale import j

JSBASE = j.application.JSBaseClass


from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from gevent import Greenlet
import gevent


class FileSystemMonitor(Greenlet, JSBASE):
    def __init__(self, syncer):
        Greenlet.__init__(self)
        self.syncer = syncer
        self.event_handler = MyFileSystemEventHandler(self.syncer)
        self.observer = Observer()
        self.event_handler = MyFileSystemEventHandler(syncer=self.syncer)

    def _run(self):

        for item in self.syncer._get_paths():
            source, dest = item
            self._log_info("monitor:%s" % source)
            self.observer.schedule(self.event_handler, source, recursive=True)
        self.observer.start()
        self._log_info("WE ARE MONITORING")

        while True:
            gevent.sleep(10)

    def __str__(self):
        return "FileSystemMonitor"


class MyFileSystemEventHandler(FileSystemEventHandler, JSBASE):
    def _init(self, syncer=None):
        assert syncer
        self.syncer = syncer

    def handler(self, event, action="copy"):
        """
        call all syncers
        :param event:
        :param action:
        :return:
        """
        self.syncer.handler(event, action=action)

    def on_moved(self, event):
        self.syncer.sync(monitor=False)
        # self.handler(event, action="delete")

    def on_created(self, event):
        self.handler(event)

    def on_deleted(self, event):
        self.handler(event, action="delete")

    def on_modified(self, event):
        self.handler(event)
