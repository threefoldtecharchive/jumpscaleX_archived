import inspect

class LoggerInstanceBase():

    def __init__(self,j,logsource_obj,logger=None):
        self._logsource_obj = logsource_obj
        self._logger = logger
        self._j = j
        self._enable = False

    def _reset(self):
        if self._logger:
            self._log__reset()


    def debug(self,msg,cat="",data=None):
        self.log(msg,cat=cat,level=10,data=data)

    def info(self,msg,cat="",data=None):
        self.log(msg,cat=cat,level=10,data=data)

    def log(self,msg,cat="",level=10,data=None):
        """

        :param msg: what you want to log
        :param cat: any dot notation category
        :param level: level of the log
        :return:

        can use {red}, {reset}, ... see color codes


        levels:

        10 = debug
        15 = stdout = print
        20 = info
        30 = error
        40 = critical

        """

        frame_ = inspect.currentframe().f_back
        fname = frame_.f_code.co_filename.split("/")[-1]
        defname = frame_.f_code.co_name
        linenr= frame_.f_code.co_firstlineno

        # while obj is None and frame_:
        #     locals_ = frame_.f_locals
        #
        #     if tbc2 in locals_:
        #         obj = locals_[tbc2]
        #     else:
        #         frame_ = frame_.f_back

        if self._logsource_obj._location:
            context = "%s:%s"%(self._logsource_obj._location,defname)
        else:
            context = "def:%s"%(defname)

        logdict={}
        logdict["linenr"] = linenr
        logdict["processid"] = self._j.application.appname
        logdict["message"] = msg
        logdict["filepath"] = fname
        logdict["level"] = level
        logdict["context"] = context
        logdict["cat"] = cat
        logdict["data"] = data

        if self._logger:
            self._log__process(logdict)

        else:
            self._j.core.tools.log2stdout(logdict)








