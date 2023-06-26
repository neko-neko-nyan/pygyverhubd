import os
import random
import sys


sys.path.append(os.path.dirname(__file__))


from gyverhubd import Device, run_server, LayoutBuilder, Layout, Color
from gyverhubd.proto.ws import WSProtocol
from gyverhubd.ui.components.button import Button, ButtonIcon
from gyverhubd.ui.components.tabs import Tabs
from gyverhubd.ui.components.text import Label, Led, Title, Gauge, Display, Html, Log, Canvas
from gyverhubd.ui.components.input import Input, Password
from gyverhubd.ui.components.spinner import Slider, Spinner
from gyverhubd.ui.components.controls import Joystick, ColorSelect, Select, Flags
from gyverhubd.ui.components.switch import Switch, SwitchIcon, SwitchText
from gyverhubd.ui.components.datetime import Date, Time, DateTime


class MyDevice(Device):
    name = "Test"
    id = '12345'

    class ui(LayoutBuilder):
        tabs = Tabs(items=("Tab 1", "MY TAB", "tab 2", "tab 3", "TAB 4"))

        b1 = Button("Button 1")
        b2 = Button("Button 2", color=Color.RED)
        b3 = ButtonIcon("")
        b4 = ButtonIcon("", color=Color.AQUA)

        l1 = Label("Status")
        led1 = Led("Status")
        led2 = Led("Icon", text="")

        t = Title("Inputs")

        i1 = Input("String input", regex="^[A-Za-z]+$")
        i2 = Input("cstring input")
        i3 = Input("int input")
        i4 = Input("float input")

        i5 = Password("Pass input", color=Color.RED)

        i6 = Slider("Slider")
        i7 = Slider("Slider F", value=10, min=0, max=90, step=0.5, color=Color.PINK)

        g = Gauge("Temp", text="°C", value=random.randrange(-5, 30), min=-5, max=30, step=0.1, color=Color.RED)

        j = Joystick(auto=True)

        s1 = Spinner("Spinner")
        s2 = Spinner("Spinner F", value=0, min=0, max=10, step=0.5)

        sw1 = Switch("My switch")
        sw2 = SwitchIcon("My switch i", text="", color=Color.BLUE)
        sw3 = SwitchText("My switch t", text="ON", color=Color.VIOLET)
        cs = ColorSelect("Color")

        date = Date("Date select", color=Color.RED)
        time = Time("Time select", color=Color.YELLOW)

        datetime = DateTime("Date time")

        sel = Select("List picker", items=["kek", "puk", "lol"])
        flags = Flags("My flags", items=["mode 1", "flag", "test"], color=Color.AQUA)

        disp = Display("", color=Color.BLUE)
        h = Html("some custom\n<strong>Text</strong>")

        log = Log("text")

        canvas = Canvas("label", width=90, height=80)

    ui: Layout


if __name__ == '__main__':
    run_server(MyDevice, protocols=[WSProtocol()])
