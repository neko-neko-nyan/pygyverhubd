from gyverhubd import Component


class Label(Component):
    __type__ = "label"
    __value_field__ = ('value', 'value', '')
    __fields__ = (
        ('size', 'size', 12),
        ('color', 'color', None),
    )


class Html(Component):
    __type__ = "html"
    __value_field__ = ('value', 'value', 0)


class Gauge(Component):
    __type__ = "gauge"
    __value_field__ = ('value', 'value', 0)
    __fields__ = (
        ('text', 'text', ""),
        ('min', 'min', 0),
        ('max', 'max', 100),
        ('step', 'step', 1),
        ('color', 'color', None),
    )


class Led(Component):
    __type__ = "led"
    __value_field__ = ('value', 'value', True)
    __fields__ = (
        ('text', 'text', ''),
    )


class Title(Component):
    __type__ = "title"


class Image(Component):
    __type__ = "image"
    __fields__ = (
        ('value', 'value', True),
    )


class Spacer(Component):
    __type__ = "spacer"
    __fields__ = (
        ('height', 'height', 0),
    )


class Stream(Component):
    __type__ = "stream"


class Js(Component):
    __type__ = "js"
    __fields__ = (
        ('value', 'value', ''),
    )


class Log(Component):
    __type__ = "log"
    __value_field__ = ('text', 'text', '')


class Display(Component):
    __type__ = "display"
    __value_field__ = ('value', 'value', '')
    __fields__ = (
        ('rows', 'rows', 1),
        ('size', 'size', 12),
        ('color', 'color', None),
    )


class Canvas(Component):
    __type__ = "canvas"
    __value_field__ = ('commands', 'value', ())
    __fields__ = (
        ('width', 'width', 100),
        ('height', 'height', 100),
        ('active', 'active', True),
    )

    async def on_event(self, value):
        value = int(value)
        x = value >> 16
        y = value & 0xffff
        value = x, y
        self._invoke_handlers(value)

    clicked = Component.changed


class Table(Component):
    __type__ = "table"
    __value_field__ = ('value', 'value', '')
    __fields__ = (
        ('align', 'align', ''),
        ('width', 'width', ''),
    )
