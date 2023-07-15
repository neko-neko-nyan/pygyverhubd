from gyverhubd import Device, run_server, download_and_update
from gyverhubd.proto.websocket import WebsocketProtocol


class MyDevice(Device):
    name = "Test OTA"
    ota_url = download_and_update
    ota_parts = ('flash', )
    update_format = "py"

    async def ota_update(self, part, data: bytes):
        print(part)
        print(data)


if __name__ == '__main__':
    run_server(MyDevice(), protocols=[WebsocketProtocol()])
