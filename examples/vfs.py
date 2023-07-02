import json
import os
import sys

sys.path.append(os.path.dirname(__file__))

from gyverhubd.proto.mqtt import MqttProtocol
from gyverhubd import Device, run_server, UnionFilesystem, VirtualFilesystem, MappedFilesystem


class MyDevice(Device):
    name = "Test VFS"

    config = {}

    fs = UnionFilesystem()\
        .add('', VirtualFilesystem())  # make root writeable for easy upload
    fs.add('/fs', MappedFilesystem('test'))

    @fs.virtual_file('/config')
    def config_vf(self):
        return json.dumps(self.config).encode()

    @config_vf.setter
    def config_vf(self, value):
        self.config = json.loads(value.decode())

    fs.map_file('/startup-config', 'config.json', allow_delete=False)


if os.path.exists('config.json'):
    with open('config.json', 'rt', encoding='utf-8') as f:
        MyDevice.config = json.load(f)


if __name__ == '__main__':
    run_server(MyDevice(), protocols=[MqttProtocol("test.mosquitto.org")])
