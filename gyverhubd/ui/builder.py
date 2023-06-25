import enum
import itertools

from gyverhubd import Color


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

    def _ensure_name(self, name: str | None) -> str:
        if name is None:
            return next(self._new_name)
        return name

    def button(self, label, size: int = 12, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="button", name=name, label=label, size=size, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value == '1'

    def button_icon(self, label, size: int = 12, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="button_i", name=name, label=label, size=size, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value == '1'

    def label(self, label, value: str = "", size: int = 12, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="label", name=name, value=value, label=label, size=size, color=color, tab_w=tab_w))

    def title(self, label):
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="title", label=label))

    def log(self, text: str, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="log", name=name, text=text, tab_w=tab_w))

    def display(self, value, rows: int = 1, size: int = 12, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="display", value=value, name=name, rows=rows, size=size, color=color, tab_w=tab_w))

    def html(self, value, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="html", value=value, name=name, tab_w=tab_w))

    def js(self, value):
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="js", value=value))

    def input(self, label, value: str = "", regex: str = "", max: int | None = None, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="input", name=name, value=value, regex=regex, label=label, max=max,
                                         color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def password(self, label, value: str = "", regex: str = "", max: int | None = None, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="pass", name=name, value=value, regex=regex, label=label, max=max,
                                         color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def spinner(self, label, value: int = 0, min: int = 0, max: int = 100, step: int = 1, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="spinner", name=name, label=label, value=value, min=min, max=max, step=step,
                                         color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def slider(self, label, value: int = 0, min: int = 0, max: int = 100, step: int = 1, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="slider", name=name, label=label, value=value, min=min, max=max, step=step,
                                         color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def gauge(self, text, label, value: int = 0, min: int = 0, max: int = 100, step: int = 1, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="gauge", name=name, text=text, label=label, value=value, min=min, max=max, step=step,
                                         color=color, tab_w=tab_w))

    def switch(self, label, value: bool = True, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="switch", name=name, label=label, value=value, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def switch_icon(self, label, text, value: bool = True, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="switch_i", name=name, label=label, text=text, value=value, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def switch_text(self, label, text, value: bool=True, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="switch_t", name=name, label=label, text=text, value=value, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def date(self, label, value: int = 0, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="date", name=name, label=label, value=value, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def time(self, label, value: int = 0, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="time", name=name, label=label, value=value, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def datetime(self, label, value: int = 0, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="datetime", name=name, label=label, value=value, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def select(self, label, text, value: int = 0, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="select", name=name, label=label, text=text, value=value, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def flags(self, label, text, value: int = 0, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="flags", name=name, label=label, text=text, value=value, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def color(self, label, value: int = 0, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="color", name=name, label=label, value=value, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def led(self, label, text="", value: bool = False, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="led", name=name, label=label, text=text, value=value, tab_w=tab_w))

    def spacer(self, height: int, tab_w=None):
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="spacer", height=height, tab_w=tab_w))

    def stream(self, height: int, tab_w=None):
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="stream", height=height, tab_w=tab_w))

    def image(self, label, prd: str, value: str, tab_w=None):
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="image", label=label, prd=prd, value=value, tab_w=tab_w))

    def joystick(self, label, auto: bool = False, exp: bool = False, color: Color | None = None, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="joy", name=name, label=label, auto=auto, exp=exp, color=color, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def tabs(self, label, value: str, text: str, tab_w=None, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="tabs", name=name, label=label, value=value, text=text, tab_w=tab_w))
        elif self._component_name == name:
            return self._value

    def menu(self, label, value: str, text: str, tab_w=None):
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="menu", name="_menu", label=label, value=value, text=text, tab_w=tab_w))
        elif self._component_name == "_menu":
            return self._value

    def canvas(self, label, width: int = 100, height: int = 100, active: bool = True, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="canvas", name=name, label=label, width=width, height=height, active=active, value=[]))
        elif self._component_name == name:
            return self._value

    def confirm(self, label, name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="confirm", name=name, label=label))
        elif self._component_name == name:
            return self._value

    def prompt(self, label, value: str = "", name=None):
        name = self._ensure_name(name)
        if self._build_type == BuildType.LAYOUT:
            self._components.append(dict(type="prompt", name=name, label=label, value=value))
        elif self._component_name == name:
            return self._value
