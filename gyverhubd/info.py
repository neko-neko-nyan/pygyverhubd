import collections
import datetime
import typing

from . import __version__, device

__all__ = ["DeviceInfo"]


class DeviceInfo:
    __slots__ = ('_data', '_handlers')

    def __init__(self):
        self._data = dict(version={}, net={}, memory={}, system={})
        self._handlers = collections.defaultdict(list)

    def to_json(self, version) -> dict[str, dict]:
        data = dict(self._data)
        for group, handlers in self._handlers.items():
            for handler in handlers:
                data[group].update(handler(device))

        data['version']['Library'] = __version__
        data['version']['Firmware'] = version
        return data

    def set(self, group: str, name: str, value: str) -> typing.Self:
        self._data[group][name] = value
        return self

    def version(self, name: str, value: str) -> typing.Self:
        return self.set('version', name, value)

    def system(self, name: str, value: str) -> typing.Self:
        return self.set('system', name, value)

    def network(self, name: str, value: str) -> typing.Self:
        return self.set('net', name, value)

    def memory(self, name: str, value: str | int, total: int | None = None) -> typing.Self:
        if isinstance(value, (tuple, list)) and total is None:
            value, total = value
        if isinstance(value, int):
            if total is None:
                total = 0
            value = [value, total]
        else:
            if total is not None:
                raise TypeError("Argument 'total' must not be set when value is str!")
        return self.set('memory', name, value)

    def uptime(self, value: datetime.timedelta) -> typing.Self:
        # noinspection PyTypeChecker
        return self.set('system', 'Uptime', value.seconds)

    def set_handler(self, group: str, fn: callable):
        self._handlers[group].append(fn)

    def handler(self, group: str):
        def _decorator(fn):
            self.set_handler(group, fn)
            return fn

        return _decorator
