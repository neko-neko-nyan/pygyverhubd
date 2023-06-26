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


class Menu(Tabs):
    __type__ = "tabs"
    name = "_menu"
