from gyverhubd import Component


class ButtonBase(Component):
    __value_field__ = ('is_pressed', None, False)
    __fields__ = (
        ('size', 'size', 12),
        ('color', 'color', None)
    )

    async def on_event(self, value):
        value = int(value)

        if value != 2:
            if type(self).__value_field__ is not None:
                setattr(self, type(self).__value_field__[0], bool(value))

        self._invoke_handlers(value)

    def pressed(self, fn):
        self.add_handler(lambda s, value: fn(s) if value == 1 else None)
        return fn

    def released(self, fn):
        self.add_handler(lambda s, value: fn(s) if value == 0 else None)
        return fn

    def clicked(self, fn):
        self.add_handler(lambda s, value: fn(s) if value == 2 else None)
        return fn


class Button(ButtonBase):
    __type__ = 'button'


class ButtonIcon(ButtonBase):
    __type__ = 'button_i'
