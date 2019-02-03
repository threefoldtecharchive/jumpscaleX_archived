from Jumpscale import j
from .LoggerInstanceBase import LoggerInstanceBase


class LoggerInstance(LoggerInstanceBase):

    def __init__(self,logsource_obj,logger=None):
        LoggerInstanceBase.__init__(self,j=j,logsource_obj,logger=logger)





