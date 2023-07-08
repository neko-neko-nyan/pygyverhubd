import collections

import inspect
import typing

__all__ = ['EventTarget']


class _Listener:
    __slots__ = ('__func', '__calls', '__total_calls')

    def __init__(self, func, calls: int = 0):
        self.__func = func
        self.__calls = calls
        self.__total_calls = 0

    async def call(self, *args, **kwargs):
        """
        call the subscribed function and returns whether future calls are available
        """
        res = self.__func(*args, **kwargs)
        if inspect.isawaitable(res):
            await res
        if self.__calls > 0:
            self.__total_calls += 1
            if self.__calls == self.__total_calls:
                return True
        return False

    def is_func(self, func):
        """
        Compares given function with the subscriber
        """
        return self.__func == func


class EventTarget:
    __slots__ = ('__events', )

    def __init__(self):
        self.__events: collections.defaultdict[str, typing.List[_Listener]] = collections.defaultdict(list)

    def on(self, event: str, calls: int = 0):
        """
        Registers a listener to an event. calls means number of maximum function calls.
        Any none positive number means infinite number of calls
        """
        def _wr(fn):
            new_listener = _Listener(fn, calls)
            self.__events[event].append(new_listener)
            return fn
        return _wr

    def add_event_listener(self, event: str, listener, calls: int = 0):
        """
        Registers a listener to an event. calls means number of maximum function calls.
        Any none positive number means infinite number of calls
        """
        new_listener = _Listener(listener, calls)
        self.__events[event].append(new_listener)

    def remove_event_listener(self, event: str, listener):
        """
        Removes a listener from an event
        """
        listeners = self.__events[event]
        for _listener in listeners:
            if _listener.is_func(listener):
                listeners.remove(_listener)

    async def dispatch_event(self, event: str, *args, **kwargs):
        """
        Triggers a given event. All registered listeners are invoked with the provided parameters
        """
        listeners = self.__events[event]
        for listener in listeners:
            calls_over = await listener.call(*args, **kwargs)
            if calls_over:
                self.__events[event].remove(listener)
