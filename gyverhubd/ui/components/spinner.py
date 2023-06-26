from gyverhubd import Component


class NumberInputBase(Component):
    __value_field__ = ('value', 'value', 0)
    __fields__ = (
        ('min', 'min', 0),
        ('max', 'max', 100),
        ('step', 'step', 1),
        ('color', 'color', None),
    )

    def event2value(self, value):
        try:
            return int(value)
        except ValueError:
            return float(value)


class Spinner(NumberInputBase):
    __type__ = "spinner"


class Slider(NumberInputBase):
    __type__ = "slider"
