from Jumpscale import j

class BuilderMonitoringFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.monitoring"

    def _init(self):
        self._logger_enable()
        from .BuilderSmartmontools import BuilderSmartmontools
        self.smartmon = BuilderSmartmontools()
        from .BuilderGrafanaFactory import BuilderGrafanaFactory
        self.grafana = BuilderGrafanaFactory()

        #TODO:*1




