import typing

from gyverhubd import Component, Color


class Select(Component):
    __type__ = "select"
    __value_field__ = ('index', 'value', 0)
    __fields__ = (
        ('items', 'text', ()),
        ('color', 'color', None),
    )

    @property
    def value(self):
        return self.items[self.index]

    def event2value(self, value: str):
        return int(value)


class Flags(Component):
    __type__ = "flags"
    __value_field__ = ('value', 'value', 0)
    __fields__ = (
        ('items', 'text', ()),
        ('color', 'color', None),
    )

    def event2value(self, value: str):
        return int(value)

    def is_enabled(self, index):
        return self.value & (1 << index) != 0


class ColorSelect(Component):
    __type__ = "color"
    __value_field__ = ('value', 'value', Color.DEFAULT)

    def event2value(self, value: str):
        return Color.from_hex(int(value))


class Joystick(Component):
    __type__ = "joy"
    __value_field__ = ('value', 'value', (0, 0))
    __fields__ = (
        ('auto', 'auto', False),
        ('exp', 'exp', False),
        ('color', 'color', None),
    )

    def event2value(self, value: str):
        value = int(value)
        y = (value & 0xFFFF) - 255
        x = (value >> 16) - 255
        return x, y

    def value2event(self, value: typing.Tuple[int, int]):
        return None
