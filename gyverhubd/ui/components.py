import dataclasses


@dataclasses.dataclass
class Component:
    def to_json(self):
        return {i: getattr(self, i) for i in dir(self) if not i.startswith('_') and i != 'to_json'}


@dataclasses.dataclass
class Button(Component):
    type = "button"
    name: str
    label: str
    size: int = 12
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class ButtonIcon(Button):
    type = "button_i"


@dataclasses.dataclass
class Label(Component):
    type = "label"
    name: str
    label: str
    value: str = ""
    size: int = 12
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Title(Component):
    type = "title"
    label: str


@dataclasses.dataclass
class Log(Component):
    type = "log"
    name: str
    text: str
    tab_w: int | None = None


@dataclasses.dataclass
class Display(Component):
    type = "display"
    name: str
    value: str
    rows: int = 1
    size: int = 12
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Html(Component):
    type = "html"
    name: str
    value: str
    tab_w: int | None = None


@dataclasses.dataclass
class Js(Component):
    type = "js"
    value: str


@dataclasses.dataclass
class Input(Component):
    type = "input"
    name: str
    label: str
    value: str = ""
    regex: str = ""
    max: int | None = None
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Password(Input):
    type = "pass"


@dataclasses.dataclass
class Spinner(Component):
    type = "spinner"
    name: str
    label: str
    value: int = 0
    min: int = 0
    max: int = 100
    step: int = 1
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Slider(Spinner):
    type = "slider"


@dataclasses.dataclass
class Gauge(Component):
    type = "gauge"
    name: str
    text: str
    value: int = 0
    min: int = 0
    max: int = 100
    step: int = 1
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Switch(Component):
    type = "switch"
    name: str
    label: str
    value: bool = True
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class SwitchIcon(Switch):
    type = "switch_i"
    text: str = ""


@dataclasses.dataclass
class SwitchText(Switch):
    type = "switch_t"
    text: str = ""


@dataclasses.dataclass
class Date(Component):
    type = "date"
    name: str
    label: str
    value: int = 0
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Time(Date):
    type = "time"


@dataclasses.dataclass
class DateTime(Date):
    type = "datetime"


@dataclasses.dataclass
class Select(Component):
    type = "select"
    name: str
    value: int
    text: str
    label: str
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Flags(Component):
    type = "flags"
    name: str
    value: int
    text: str
    label: str
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Color(Component):
    type = "color"
    name: str
    value: int
    label: str
    tab_w: int | None = None


@dataclasses.dataclass
class Led(Component):
    type = "led"
    name: str
    value: str
    label: str
    text: str
    tab_w: int | None = None


@dataclasses.dataclass
class Spacer(Component):
    type = "spacer"
    height: int
    tab_w: int | None = None


@dataclasses.dataclass
class Tabs(Component):
    type = "tabs"
    name: str
    value: str
    text: str
    label: str
    tab_w: int | None = None


@dataclasses.dataclass
class Menu(Tabs):
    type = "menu"
    name = "_menu"


@dataclasses.dataclass
class Image(Component):
    type = "image"
    value: str
    prd: str
    label: str = ""
    tab_w: int | None = None


@dataclasses.dataclass
class Stream(Component):
    type = "stream"
    tab_w: int | None = None


@dataclasses.dataclass
class Joy(Component):
    type = "joy"
    name: str
    auto: bool
    exp: bool
    label: str
    color: int | None = None
    tab_w: int | None = None


@dataclasses.dataclass
class Confirm(Component):
    type = "confirm"
    name: str
    label: str


@dataclasses.dataclass
class Prompt(Component):
    type = "prompt"
    name: str
    value: str
    label: str


@dataclasses.dataclass
class Canvas(Component):
    type = "canvas"
    name: str
    width: str
    height: str
    label: str
    active: bool
    value: list[Component]
