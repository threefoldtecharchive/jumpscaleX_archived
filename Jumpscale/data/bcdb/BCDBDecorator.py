
from gevent.event import Event
from Jumpscale import j

#will make sure that every decorated method get's execute one after the other

skip_for_debug = True

def queue_method(func):
    def wrapper_queue_method(*args, **kwargs):
        self=args[0]
        if self.bcdb.dataprocessor_greenlet is None:
            self.bcdb.dataprocessor_start()
        self._logger.debug(str(func))
        if skip_for_debug or "noqueue" in kwargs:
            if "noqueue" in kwargs:
                kwargs.pop("noqueue")
            res = func(*args,**kwargs)
            return res
        else:
            event=Event()
            j.data.bcdb.latest.queue.put((func,args,kwargs, event,None))
            event.wait(1000.0) #will wait for processing
            self._logger.debug("OK")
            return
    return wrapper_queue_method

def queue_method_results(func):
    def wrapper_queue_method(*args, **kwargs):
        self=args[0]
        if self.bcdb.dataprocessor_greenlet is None:
            self.bcdb.dataprocessor_start()
        self._logger.debug(str(func))
        if skip_for_debug or  "noqueue" in kwargs:
            if "noqueue" in kwargs:
                kwargs.pop("noqueue")
            res = func(*args,**kwargs)
            return res
        else:
            event=Event()
            id = j.data.bcdb.latest.results_id+1  #+1 makes we have copy
            if id == 100000:
                id = 0
                self.results_id = 0
            j.data.bcdb.latest.results_id+=1
            j.data.bcdb.latest.queue.put((func,args,kwargs, event,id))
            event.wait(1000.0) #will wait for processing
            self._logger.debug("OK")
            res = j.data.bcdb.latest.results[id]
            j.data.bcdb.latest.results.pop(id)
            return res
    return wrapper_queue_method
