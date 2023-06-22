from gyverhubd import Device, run_server
from gyverhubd.proto.ws import WSProtocol


class MyDevice(Device):
    name = "Test"
    id = '12345'

    def build_ui(self, ui):
        pass


if __name__ == '__main__':
    run_server(MyDevice, protocols=[WSProtocol()])
