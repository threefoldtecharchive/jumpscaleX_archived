import logging


class JSLogger(logging.Logger):

    def __init__(self, name, factory):
        super(JSLogger, self).__init__(name)
        self.level = 10         #https://docs.python.org/3/library/logging.html#levels  10 is debug
        self.DEFAULT = False
        # self.custom_filters = {}
        # self.__only_me = False
        self.factory = factory
        self._j = factory._j
        # print("LOGGER")

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)

        """
        j = self._j
        if not self.isEnabledFor(logging.ERROR):
            return
        # issue #83 and #81 - error API has now changed.  TODO: escalate
        # eco = j.errorhandler.getErrorConditionObject(
        #     ddict={}, msg=msg, msgpub=msg, category=self.name,
        #     level=logging.ERROR, type=logging.getLevelName(logging.ERROR),
        #     tb=None, tags='')
        # j.errorhandler._send2Redis(eco)

        self._log(logging.ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        j = self._j
        if not self.isEnabledFor(logging.CRITICAL):
            return
        # issue #83 and #81 - error API has now changed.  TODO: escalate
        # eco = j.errorhandler.getErrorConditionObject(
        #     ddict={}, msg=msg, msgpub=msg, category=self.name,
        #     level=logging.CRITICAL, type=logging.getLevelName(
        #         logging.CRITICAL),
        #     tb=None, tags='')
        # j.errorhandler._send2Redis(eco)

        self._log(logging.CRITICAL, msg, args, **kwargs)

    # def enable_only_me(self):
    #     """
    #     Enable filtering. Output only log from this logger and its children.
    #     Logs from other modules are masked
    #     """
    #     if not self.__only_me and 'console' in j.logger.handlers:
    #         only_me_filter = logging.Filter(self.name)
    #         j.logger.handlers['console'].addFilter(only_me_filter)
    #         self.custom_filters["only_me"] = only_me_filter
    #         self.__only_me = True

    # def disable_only_me(self):
    #     """
    #     Disable filtering on only this logger
    #     """
    #     if self.__only_me and 'console' in j.logger.handlers:
    #         j.logger.handlers['console'].removeFilter(
    #             self.custom_filters['only_me'])
    #         self.__only_me = False

    # def __str__(self):
    #     return "LOGGER:%s:%s"%(self.name,self.level)
    #
    # __repr__ = __str__
