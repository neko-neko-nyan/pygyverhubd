import os
import random
import sys


sys.path.append(os.path.dirname(__file__))


from gyverhubd import Device, run_server, DeviceInfo
from gyverhubd.proto.ws import WSProtocol


class MyDevice(Device):
    name = "Test"

    info = DeviceInfo()
    info.version("My component", "1.0")
    info.system("CPU", "AMD EPYC 9654 😱")
    info.network("IP", "192.168.0.123")
    info.memory("HDD", "64 TB")
    info.memory("SSD", 2 * 1024 * 1024 * 1024 * 1024)

    @info.handler('memory')
    def _(self):
        total_ram = 1024 * 1024 * 1024 * 64
        used_ram = random.randrange(total_ram * 1 // 8, total_ram * 7 // 8)
        return {
            'RAM': [used_ram, total_ram]
        }


if __name__ == '__main__':
    run_server(MyDevice(), protocols=[WSProtocol()])
