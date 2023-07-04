import os
import sys

from gyverhubd.proto.ws import WSProtocol

sys.path.append(os.path.dirname(__file__))

from gyverhubd.proto.mqtt import MqttProtocol
from gyverhubd import Device, run_server, download_and_update


class MyDevice(Device):
    name = "Test OTA"
    ota_url = download_and_update
    ota_parts = ('flash', )
    update_format = "py"

    async def ota_update(self, part, data: bytes):
        print(part)
        print(data)


if __name__ == '__main__':
    run_server(MyDevice(), protocols=[WSProtocol()])
