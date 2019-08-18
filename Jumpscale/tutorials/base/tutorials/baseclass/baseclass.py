from Jumpscale import j
import time

JSBASE = j.application.JSBaseClass


# next will be filled in by the template engine when this example is called
name = "{{name}}"

# something = "{{j.data.time.epoch}}"


class TutorialCacheClass(j.application.JSBaseClass):
    """
    """

    def __init__(self):
        JSBASE.__init__(self)
        self.value = 1

    def amounts_servers_active(self, reload=False):
        def do(me=None):
            print("self.value:%s" % me.value)
            # SLOW FUNCTION
            # Get something from webservice but it could fail
            # ok to cache for 60 sec
            x = j.data.idgenerator.generateRandomInt(1, 5)
            print(x)
            if x == 2:
                # simulator that once and a while I get the return from internet, here 1 time on 10 it works
                return me.value
            else:
                msg = "could not fetch info, there was simulated network error"
                print(msg)
                time.sleep(0.05)
                raise j.exceptions.Base(msg)

        return self._cache.get("amounts_servers_active", do, expire=60, retry=100, refresh=reload, me=self)

    def logger_test(self):
        self._log_info("info")
        self._log_warning("warning")
        self._log_error("error")
        self._log_debug("debug")

    def get_dir_path(self):
        self._log_debug("should show path in codegenerator dir")
        self._log_info(self._dirpath)
        self._log_debug("lets see path of a module in jumpscale")
        self._log_info(j.tools.dnstools._dirpath)


def main():

    c = TutorialCacheClass()
    c.cache.reset()
    c.value = 1
    print("FIRST QUERY, value needs to be 1")
    assert c.amounts_servers_active() == 1
    c.value = 2

    c.logger_test()
    c._logger_enable()
    print("NOW LOGGING ENABLED")
    c.logger_test()

    c.get_dir_path()

    j.shell()
