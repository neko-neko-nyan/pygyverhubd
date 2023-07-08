from gyverhubd import Component


class ButtonBase(Component):
    __value_field__ = ('is_pressed', None, False)
    __fields__ = (
        ('size', 'size', 12),
        ('color', 'color', None)
    )

    def pressed(self, fn):
        self.add_handler(lambda s, value: fn(s) if value == '1' else None)
        return fn

    def released(self, fn):
        self.add_handler(lambda s, value: fn(s) if value == '0' else None)
        return fn

    clicked = pressed


class Button(ButtonBase):
    __type__ = 'button'


class ButtonIcon(ButtonBase):
    __type__ = 'button_i'
