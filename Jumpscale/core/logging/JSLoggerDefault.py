import logging

# from pprint import pprint as print

class JSLoggerDefault(logging.Logger):

    def __init__(self, name, factory):
        super(JSLoggerDefault, self).__init__(name)
        self.level=20
        self.DEFAULT = True
        # print("DEFAULT:%s"%name)
        self.factory = factory
        self._j = self.factory._j

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)

        """
        j = self._j
        if self.isEnabledFor(logging.ERROR):
            eco = j.errorhandler.getErrorConditionObject(
                ddict={}, msg=msg, msgpub=msg, category=self.name,
                level=logging.ERROR, type=logging.getLevelName(logging.ERROR),
                tb=None, tags='')
            j.errorhandler._send2Redis(eco)

            self._log(logging.ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        j = self._j
        if self.isEnabledFor(logging.CRITICAL):
            eco = j.errorhandler.getErrorConditionObject(
                ddict={}, msg=msg, msgpub=msg, category=self.name,
                level=logging.CRITICAL, type=logging.getLevelName(
                    logging.CRITICAL),
                tb=None, tags='')
            j.errorhandler._send2Redis(eco)

            self._log(logging.CRITICAL, msg, args, **kwargs)


    # def error(self, msg, *args, **kwargs):
    #     """
    #     """
    #     self._j.logger.logger.error(msg)

    # def critical(self, msg, *args, **kwargs):
    #     """
    #     """
    #     self._j.logger.logger.critical(msg)

    def info(self, msg, *args, **kwargs):
        print ("* %s"%msg)

    def debug(self, *args, **kwargs):
        pass

    def fatal(self, msg, *args, **kwargs):
        raise RuntimeError(msg)

    def __str__(self):
        return "DEFAULT LOGGER"

    __repr__ = __str__
