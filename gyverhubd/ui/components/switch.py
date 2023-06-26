from gyverhubd import Component


class SwitchBase(Component):
    __value_field__ = ('value', 'value', True)
    __fields__ = (
        ('color', 'color', None),
    )

    def event2value(self, value):
        return value == '1'


class Switch(SwitchBase):
    __type__ = "switch"


class SwitchIcon(SwitchBase):
    __type__ = "switch_i"
    __fields__ = (
        ('text', 'text', ""),
    )


class SwitchText(SwitchBase):
    __type__ = "switch_t"
    __fields__ = (
        ('text', 'text', ""),
    )
