from Jumpscale import j


def property_js(func):
    def wrapper_action(*args, **kwargs):
        self=args[0]
        args=args[1:]
        self._log_debug(str(func))
        if self._running is None:
            self.service_manage()
        name= func.__name__
        if skip_for_debug or "noqueue" in kwargs:
            if "noqueue" in kwargs:
                kwargs.pop("noqueue")
            res = func(*args,**kwargs)
            return res
        else:
            event=Event()
            action=self._action_new(name=name,args=args,kwargs=kwargs)
            self.action_queue.put((func,args,kwargs,event,action.id))
            event.wait(1000.0) #will wait for processing
            res = j.data.serializers.msgpack.loads(action.result)
            self._log_debug("METHOD EXECUTED OK")
            return action
    return wrapper_action

