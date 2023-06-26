import collections
import datetime
import typing


class DeviceInfo:
    __slots__ = ('_data', '_handlers', '_device')

    def __init__(self):
        self._data = dict(version={}, net={}, memory={}, system={})
        self._handlers = collections.defaultdict(list)
        self._device = None

    def __get__(self, instance, owner=None):
        if self._device is None:
            obj = type(self)
            obj._data = self._data
            obj._handlers = self._handlers
            obj._device = instance
            return obj
        return self

    def to_json(self) -> dict[str, dict]:
        data = dict(self._data)
        for group, handlers in self._handlers.items():
            for handler in handlers:
                data[group].update(handler(self._device))
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
        return self.set('system', 'Uptime', value.seconds)

    def set_handler(self, group: str, fn: callable):
        self._handlers[group].append(fn)

    def handler(self, group: str):
        def _decorator(fn):
            self.set_handler(group, fn)
            return fn
        return _decorator

    # version: dict[str, str] = dataclasses.field(default_factory=dict)  # Library, Firmware
    # net: dict[str, str] = dataclasses.field(default_factory=dict)  # Mode, MAC, SSID, RSSI, IP
    # memory: dict[str, tuple[int, int] | str] = dataclasses.field(default_factory=dict)  # RAM Flash Sketch
    # system: dict[str, str] = dataclasses.field(default_factory=dict)  # Uptime (int), Model, CPU_Mhz Flash_chip
