import random

from gyverhubd import Device, run_server, Builder
from gyverhubd.proto.ws import WSProtocol


class MyDevice(Device):
    name = "Test"
    id = '12345'

    async def build_ui(self, ui: Builder):
        ui.tabs("", "0", "Tab 1,MY TAB,tab 2,tab 3,TAB 4")

        ui.button("Button 1")
        ui.button("Button 2", color=0xcb2839)
        ui.button_icon("")
        ui.button_icon("", color=0x2ba1cd)

        ui.label("Status")
        ui.led("Status")
        ui.led("Icon", "")

        ui.title("Inputs")

        ui.input("String input", regex="^[A-Za-z]+$")
        ui.input("cstring input")
        ui.input("int input")
        ui.input("float input")

        ui.password("Pass input", color=0xcb2839)

        ui.slider("Slider")
        ui.slider("Slider F", 0, 10, 90, 0.5, color=0xc8589a)

        ui.gauge("°C", "Temp", random.randrange(-5, 30), -5, 30, 0.1, color=0xcb2839)

        # joystick

        ui.spinner("Spinner")
        ui.spinner("Spinner F", 0, 0, 10, 0.5)

        ui.switch("My switch")
        ui.switch_icon("My switch i", "", color=0x297bcd)
        ui.switch_text("My switch t", "ON", color=0x825ae7)
        ui.color("Color")

        ui.date("Date select", color=0xcb2839)
        ui.time("Time select", color=0xd69d27)

        ui.datetime("Date time")

        ui.select("List picker", "kek,puk,lol")
        ui.flags("My flags", "mode 1,flag,test", color=0x2ba1cd)

        ui.display("", color=0x297bcd)
        ui.html("some custom\n<strong>Text</strong>")

        ui.log("text")

        ui.canvas("label", 90, 80, True)


if __name__ == '__main__':
    run_server(MyDevice, protocols=[WSProtocol()])
