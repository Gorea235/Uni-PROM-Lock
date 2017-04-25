class EventException(Exception):
    def __init__(self, funcex, msg=None):
        self._message = msg if msg is not None else "One or more exceptions occured while firing the event"
        self._exc = funcex
    
    def __repr__(self):
        return "{} (Function exceptions: {})".format(self._message, ",".join(self._exc))

class Event:
    """
    A simple class that handles a list of functions that can
    all be called by raising the event. Handlers are added and
    removed using the following notation respectively:
    event += func OR event.bind(func)
    event -= func OR event.unbind(func)
    When the event is raised, all the arguments passed are passed
    straight to the functions that are called. 
    """
    
    def __init__(self):
        self._event_funcs = {}

    def bind(self, func):
        assert callable(func)
        hsh = str(hash(func))
        if hsh in self._event_funcs.keys():
            raise KeyError("Function {} already registered to event".format(func.__name__))
        self._event_funcs[hsh] = func

    def unbind(self, func):
        assert callable(func)
        hsh = str(hash(func))
        if hsh not in self._event_funcs.keys():
            raise KeyError("Function {} not registered to event".format(func.__name__))
        del self._event_funcs[hsh]
    
    def __iadd__(self, func):
        self.bind(func)
        return self
    
    def __isub__(self, func):
        self.unbind(func)
        return self
    
    def fire(self, *args, **kwargs):
        """
        Fires the event and calls each function with the
        variables in args and kwargs.
        """
        exc = []
        for f in self._event_funcs.values():
            try:
                f(*args, **kwargs)
            except Exception as ex:
                exc.append(ex)
        if len(exc) > 0:
            raise EventException(exc)
