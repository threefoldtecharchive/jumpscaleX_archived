import time
from Jumpscale import j
JSBASE = j.application.JSBaseClass

class TIMER(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.tools.timer"
        JSBASE.__init__(self)

    @staticmethod
    def execute_until(callback, timeout=60, interval=0.2):
        """
        Check periodicly if callback function returns True

        :param callback: Callback function
        :type callback: callable
        :param timeout: Amount of time to keep checing in seconds
        :type timeout: int
        :param interval: Pause time inbetween calling the callback
        :type interval: float
        :return boolean indicating callback was returned true
        :rtype boolean
        """
        start = time.time()
        while start + timeout > time.time():
            result = callback()
            if result:
                return result
            time.sleep(interval)
        return False

    @staticmethod
    def start(cat="",memory=False):
        """

        :param cat: name for your measurment
        :param memory: if memory needs to be tracked
        :return:
        """
        TIMER._cat = cat
        TIMER.clean()
        TIMER._start = time.time()
        if memory:
            TIMER._memory = j.application.getMemoryUsage()
        else:
            TIMER._memory = None

    @staticmethod
    def stop(nritems=0, log=True):
        if TIMER._memory:
            TIMER._memory_stop = j.application.getMemoryUsage()
        TIMER._stop = time.time()
        TIMER.duration = TIMER._stop - TIMER._start
        if nritems > 0:
            TIMER.nritems = float(nritems)
            if TIMER.duration > 0:
                TIMER.performance = float(nritems) / float(TIMER.duration)
            if TIMER._memory:
                TIMER.memory_used = TIMER._memory_stop  - TIMER._memory
                TIMER.memory_peritem = float((TIMER._memory_stop * 1000 - TIMER._memory * 1000)) / float(nritems)
        if log:
            TIMER.result()
        return TIMER.performance

    @staticmethod
    def clean():
        TIMER._stop = 0.0
        TIMER._start = 0.0
        TIMER.duration = 0.0
        TIMER.performance = 0.0
        TIMER.nritems = 0.0
        TIMER.memory_used = 0.0
        TIMER.memory_peritem = 0.0


    @staticmethod
    def result():
        if TIMER._cat !="":
            print("\nDURATION FOR:%s"%TIMER._cat)
        print(("duration:%s" % TIMER.duration))
        print(("nritems:%s" % TIMER.nritems))
        print(("performance:%s/sec" % int(TIMER.performance)))
        if TIMER._memory:
            print("memory used: %s"%TIMER.memory_used)
            print("memory per item (bytes): %s"%TIMER.memory_peritem)

    def test(self):
        """
        js_shell 'j.tools.timer.test()'
        """

        j.tools.timer.start("something")
        for i in range(20):
            time.sleep(0.1)
        j.tools.timer.stop(20)
