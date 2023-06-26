from gyverhubd import Component, response
from . import DeviceUi


class Layout(DeviceUi):
    def __init__(self, components: list[Component]):
        self.components = components

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
            components.append(i.to_json())
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


class LayoutBuilderMeta(type):
    def __new__(cls, name, bases, namespace):
        if not bases:
            return super().__new__(cls, name, bases, namespace)

        components = []
        for k, v in namespace.items():
            if not k.startswith('_') and isinstance(v, Component):
                components.append(v)

        layout = Layout(components)

        for k, v in namespace.items():
            if not k.startswith('_') and isinstance(v, Component):
                v.__set_name__(layout, k)
                setattr(layout, k, v)

        return layout


class LayoutBuilder(metaclass=LayoutBuilderMeta):
    pass
