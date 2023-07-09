import contextlib
import itertools
import typing

from . import DeviceUi, Component
from .. import response

__all__ = ["Layout"]


class Layout(DeviceUi):
    def __init__(self, components: typing.List[Component] = None):
        if components is None:
            components = []

        self.components = components
        self._new_name = (f"u{i}" for i in itertools.count())

    def __new__(cls, components: typing.List[Component] = None):
        self = super().__new__(cls)
        if callable(components):
            self.__init__()
            self = self(components)
        return self

    def __getattr__(self, item):
        from . import components
        item = getattr(components, item)

        def class_wrapper(*args, **kwargs):
            el: Component = item(*args, **kwargs)
            el.__set_name__(self, next(self._new_name))
            self.components.append(el)
            return el

        return class_wrapper

    def __call__(self, fn):
        return _DeviceDescriptor(self, fn)

    @contextlib.contextmanager
    def rows(self, width=None, cols=None, height=0):
        if cols is not None:
            if width is not None:
                raise ValueError("Width and cols cannot be used together")
            width = 100 // cols

        self.components.append(_BeginWidgets(height=height))

        saved, self.components = self.components, []
        yield
        cs, self.components = self.components, saved

        self.components += cs
        self.components.append(_EndWidgets())

        if width is not None:
            tab_w = width
            for i in cs:
                i.tab_w = tab_w

    def _rebuild_required(self):
        return any((i.rebuild_required() for i in self.components))

    def _to_updates(self):
        updates = {}
        for i in self.components:
            update = i.to_update()
            if update is not None:
                updates[i.name] = update

        if not updates:
            return None
        return updates

    def _to_json(self):
        components = []
        for i in self.components:
            data = i.to_json()
            if i.__enabled__:
                components.append(data)
        return components

    async def _on_event(self, name, value):
        for i in self.components:
            if i.name == name:
                await i.on_event(value)

    async def on_update(self) -> dict:
        return response("ui", controls=self._to_json())

    async def on_ui_event(self, name: str, value: str) -> dict:
        await self._on_event(name, value)
        if self._rebuild_required():
            return response("ui", controls=self._to_json())

        updates = self._to_updates()

        if self._rebuild_required():
            return response("ui", controls=self._to_json())

        if updates is not None:
            return response("update", updates=updates)

        return response("OK")


class _DeviceDescriptor:
    def __init__(self, layout, fn):
        self._layout = layout
        self._fn = fn
        self._created = False

    def __get__(self, instance, owner=None):
        if owner is None:
            return self

        if not self._created:
            self._fn(instance, self._layout)
            self._created = True
        return self._layout


class _BeginWidgets(Component):
    __type__ = "widget_b"
    __fields__ = (
        ('height', 'height', 0),
    )


class _EndWidgets(Component):
    __type__ = "widget_e"
