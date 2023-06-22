from gyverhubd import Device, run_server, Builder
from gyverhubd.proto.ws import WSProtocol


class MyDevice(Device):
    name = "Test"
    id = '12345'

    async def build_ui(self, ui: Builder):
        if ui.button("Button 1"):
            await self.send_alert("Button 1 was clicked!")

        if ui.button("Button 2"):
            await self.send_push("Button 2 was clicked!")

        if ui.button("Button 3"):
            await self.send_notice("Button 3 was clicked!", 0xFFFFFF)


if __name__ == '__main__':
    run_server(MyDevice, protocols=[WSProtocol()])
