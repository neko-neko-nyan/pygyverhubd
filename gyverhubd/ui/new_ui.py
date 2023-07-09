import contextlib
import itertools

from . import Layout, components, Component


class Builder:
    def __init__(self):
        self.layout = Layout()
        self._new_name = (f"u{i}" for i in itertools.count())

    def __getattr__(self, item):
        item = getattr(components, item)

        def class_wrapper(*args, **kwargs):
            el: Component = item(*args, **kwargs)
            el.__set_name__(self.layout, next(self._new_name))
            self.layout.components.append(el)
            return el

        return class_wrapper

    @contextlib.contextmanager
    def rows(self, width=None, cols=None, height=0):
        if cols is not None:
            if width is not None:
                raise ValueError("Width and cols cannot be used together")
            width = 100 // cols

        self.layout.components.append(BeginWidgets(height=height))

        saved, self.layout.components = self.layout.components, []
        yield
        cs, self.layout.components = self.layout.components, saved

        self.layout.components += cs
        self.layout.components.append(EndWidgets())

        if width is not None:
            tab_w = width
            for i in cs:
                i.tab_w = tab_w


class BeginWidgets(Component):
    __type__ = "widget_b"
    __fields__ = (
        ('height', 'height', 0),
    )


class EndWidgets(Component):
    __type__ = "widget_e"


def new_ui_builder(fn):
    builder = Builder()
    fn(builder)
    return builder.layout
