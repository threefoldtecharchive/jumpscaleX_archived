import logging
import time
import os

try:
    import ujson as json
except:
    import json

import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import MemoryHandler

# XXX not used? from .Filter import ModuleFilter
from .LimitFormatter import LimitFormatter
import inspect
# FILE_FORMAT = '%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)-8s - %(message)s'


class Handlers():

    def __init__(self,j):
        self._j = j 
        self._fileRotateHandler = None
        self._consoleHandler = None
        self._memoryHandler = None
        self._telegramHandler = None
        self._all = []

    @property
    def fileRotateHandler(self, name='jumpscale'):
        if self._fileRotateHandler is None:
            if not self._j.sal.fs.exists("%s/log/" % self._j.dirs.VARDIR):
                self._j.sal.fs.createDir("%s/log/" % self._j.dirs.VARDIR)
            filename = "%s/log/%s.log" % (self._j.dirs.VARDIR, name)
            formatter = logging.Formatter(self._j.core.myenv.FORMAT_LOG)
            fh = TimedRotatingFileHandler(
                filename, when='D', interval=1, backupCount=7, encoding=None, delay=False, utc=False, atTime=None)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self._fileRotateHandler = fh
            self._all.append(self._fileRotateHandler)
        return self._fileRotateHandler

    @property
    def consoleHandler(self):
        if self._consoleHandler is None:
            formatter = self._j.core.tools._LogFormatter()
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self._consoleHandler = ch
            self._all.append(self._consoleHandler)
        return self._consoleHandler

    def redisHandler(self, redis_client=None):
        if redis_client is None:
            redis_client = self._j.core.db
        return RedisHandler(redis_client,j=self._j)

    @property
    def memoryHandler(self):
        if self._memoryHandler is None:
            self._memoryHandler = MemoryHandler(capacity=10000)
            self._all.append(self._memoryHandler)
        return self._memoryHandler

    def telegramHandler(self, client, chat_id, level=logging.CRITICAL):
        """
        Create a telegram handler to forward logs to a telegram group.
        @param client: A jumpscale telegram_bot client
        @param chat_id: Telegram chat id to which logs need to be forwarded
        @param level: Loglevel that should be handeld by this handler
        """
        if self._telegramHandler is None:
            self._telegramHandler = TelegramHandler(client, chat_id)
            self._telegramHandler.setLevel(level)
            self._telegramHandler.setFormatter(TelegramFormatter())
            self._all.append(self._telegramHandler)
        return self._telegramHandler


class RedisHandler(logging.Handler):
    """
    Handler to forward logs to a redis server
    send to the server

    ## dict keys:

    - processid : a string id can be a pid or any other identification of the log
    - cat   : optional category for log
    - level : levels see https://docs.python.org/3/library/logging.html#levels
    - linenr : nr in file where log comes from
    - filepath : path where the log comes from
    - context : where did the message come from e.g. def name
    - message : content of the message
    - data : additional data e.g. stacktrace, depending context can be different
    - hash: optional, 16-32 bytes unique for this message normally e.g. md5 of eg. concatenation of important fields

    ### lOGGING LEVELS:

    - CRITICAL 	50
    - ERROR 	40
    - WARNING 	30
    - INFO 	    20
    - DEBUG 	10
    - NOTSET 	0


    """

    def __init__(self, redis_client,j):
        """
        """
        self._j = j
        super(RedisHandler, self).__init__()
        self.redis_client = redis_client

        _dirpath = os.path.dirname(inspect.getfile(self.__class__))

        lua_path = "%s/log.lua"%_dirpath

        dd = self.redis_client.storedprocedure_register("log",0,lua_path)

        self._send("log started",context="redishandler")

    def emit(self, record):

        if record.levelno>39:
            from pudb import set_trace; set_trace()
        if record.args != ():
            from pudb import set_trace; set_trace()

        self._send(record.msg,linenr=record.lineno,filepath=record.filename,
                   level=record.levelno,context=record.funcName)

    def _send(self,message,linenr=0,filepath="",level=10,context=""):

        record2={}
        record2["linenr"] = linenr
        record2["processid"] = self._j.application.appname
        record2["message"] = message
        record2["filepath"] = filepath
        record2["level"] = level
        record2["context"] = context
        record3 = json.dumps(record2)
        self.redis_client.storedprocedure_execute("log",record3)
        # self.redis_client.storedprocedure_debug("log","'%s'"%record3)




class TelegramHandler(logging.Handler):
    """
    Handler to forward logs to a telegram group
    """

    def __init__(self, client, chat_id):
        """
        Create a telegram handler to forward logs to a telegram group.
        @param client: A jumpscale telegram_bot client
        @param chat_id: Telegram chat id to which logs need to be forwarded
        """
        super(TelegramHandler, self).__init__()
        self.telegram_client = client
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.telegram_client.send_message(self.chat_id, log_entry, parse_mode="Markdown")


class TelegramFormatter(logging.Formatter):

    def format(self, record):
        return "```\n%s\n```" % super(TelegramFormatter, self).format(record)
