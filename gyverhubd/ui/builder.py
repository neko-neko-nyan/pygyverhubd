import enum
import itertools


class BuildType(enum.Enum):
    LAYOUT = enum.auto()
    ACTION = enum.auto()


class Builder:
    def __init__(self, name=None, value=None):
        self._build_type = BuildType.LAYOUT if name is None else BuildType.ACTION
        self._component_name = name
        self._value = value

        self._components = []
        self._new_name = (f"u{i}" for i in itertools.count())

    def button(self, label, size: int = 12, color=None, tab_w=None, name=None):
        if name is None:
            name = next(self._new_name)

        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(
                type="button",
                name=name, label=label, size=size, color=color, tab_w=tab_w
            ))
        elif self._component_name == name:
            return self._value == '1'
