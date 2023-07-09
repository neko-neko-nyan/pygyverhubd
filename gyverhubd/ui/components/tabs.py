from gyverhubd import Component, ChangeType


class Tabs(Component):
    __type__ = "tabs"
    __value_field__ = ('index', 'value', 0)
    __fields__ = (
        ('items', 'text', ()),
    )

    @property
    def value(self):
        return self.items[self.index]

    def event2value(self, value: str):
        return int(value)

    def to_update(self):
        res = super().to_update()
        if res is not None:
            self.__changed__ = ChangeType.FULL

    def tab(self, name: str):
        index = len(self.items)
        self.items = (*self.items, name)
        tab = _Tab(self, index)
        return tab


class _Tab:
    def __init__(self, tabs: Tabs, index: int):
        self._tabs = tabs
        self._index = index
        self._components = []
        self._saved = None

        @tabs.changed
        def _(_, value):
            if value == index:
                self.set()
            else:
                self.unset()

    def set(self):
        for i in self._components:
            i.__enabled__ = True

    def unset(self):
        for i in self._components:
            i.__enabled__ = False

    def __enter__(self):
        self._saved = self._tabs.__layout__.components
        self._tabs.__layout__.components = self._components

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tabs.__layout__.components = self._saved
        self._saved = None
        self._tabs.__layout__.components += self._components
        self.unset()


class Menu(Tabs):
    __type__ = "tabs"
    name = "_menu"
