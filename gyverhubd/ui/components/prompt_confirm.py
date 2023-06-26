from gyverhubd import Component


class Confirm(Component):
    __type__ = "confirm"


class Prompt(Component):
    __type__ = "prompt"
    __value_field__ = ('value', 'value', '')
