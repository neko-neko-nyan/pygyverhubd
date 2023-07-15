from gyverhubd import Device, run_server
from gyverhubd.proto.mqtt import MqttProtocol
from gyverhubd.proto.websocket import WebsocketProtocol


class MyDevice1(Device):
    name = "Test1"


class MyDevice2(Device):
    name = "Test2"


if __name__ == '__main__':
    run_server(MyDevice1(), MyDevice2(), protocols=[MqttProtocol("test.mosquitto.org"), WebsocketProtocol()])
