from gyverhubd import Component


class InputBase(Component):
    __value_field__ = ('value', 'value', '')
    __fields__ = (
        ('regex', 'regex', ''),
        ('max', 'max', None),
        ('color', 'color', None),
    )


class Input(InputBase):
    __type__ = 'input'


class Password(InputBase):
    __type__ = 'pass'
