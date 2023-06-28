import random
import sys
import os

sys.path.append(os.path.dirname(__file__))


from gyverhubd import Device, run_server, Builder, Color, ui_builder
from gyverhubd.proto.ws import WSProtocol


class MyDevice(Device):
    name = "Test"

    @ui_builder
    async def ui(self, ui: Builder):
        ui.tabs("", "0", "Tab 1,MY TAB,tab 2,tab 3,TAB 4")

        ui.button("Button 1")
        ui.button("Button 2", color=Color.RED)
        ui.button_icon("")
        ui.button_icon("", color=Color.AQUA)

        ui.label("Status")
        ui.led("Status")
        ui.led("Icon", "")

        ui.title("Inputs")

        ui.input("String input", regex="^[A-Za-z]+$")
        ui.input("cstring input")
        ui.input("int input")
        ui.input("float input")

        ui.password("Pass input", color=Color.RED)

        ui.slider("Slider")
        ui.slider("Slider F", 0, 10, 90, 0.5, color=Color.PINK)

        ui.gauge("°C", "Temp", random.randrange(-5, 30), -5, 30, 0.1, color=Color.RED)

        # joystick

        ui.spinner("Spinner")
        ui.spinner("Spinner F", 0, 0, 10, 0.5)

        ui.switch("My switch")
        ui.switch_icon("My switch i", "", color=Color.BLUE)
        ui.switch_text("My switch t", "ON", color=Color.VIOLET)
        ui.color("Color")

        ui.date("Date select", color=Color.RED)
        ui.time("Time select", color=Color.YELLOW)

        ui.datetime("Date time")

        ui.select("List picker", "kek,puk,lol")
        ui.flags("My flags", "mode 1,flag,test", color=Color.AQUA)

        ui.display("", color=Color.BLUE)
        ui.html("some custom\n<strong>Text</strong>")

        ui.log("text")

        ui.canvas("label", 90, 80, True)


if __name__ == '__main__':
    run_server(MyDevice, protocols=[WSProtocol()])
