import asyncio
import json

import serial
import serial_asyncio

from . import Protocol, Request

__all__ = ["SerialProtocol", "protocol_factory"]


class SerialRequest(Request):
    def __init__(self, protocol, data):
        self.protocol: SerialProtocol = protocol

        assert isinstance(data, str) and data and data[-1] == '\0'
        url, eq, data = data[:-1].partition('=')
        super().__init__(url, data if eq else None)

    async def respond(self, data: dict):
        if self.did is not None:
            data['id'] = self.did
        await self.protocol.send(data)

    def set_focused(self, value: bool):
        self.protocol.focused = value


class SerialProtocol(Protocol):
    def __init__(self, port: str = None, baudrate: int = 9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None,
                 dsrdtr=False, inter_byte_timeout=None, exclusive=None):
        self._reader = self._writer = None
        self._kwargs = dict(url=port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits,
                            timeout=timeout, write_timeout=write_timeout, inter_byte_timeout=inter_byte_timeout,
                            xonxoff=xonxoff, rtscts=rtscts, dsrdtr=dsrdtr, exclusive=exclusive)
        self.focused = False

    def bind(self, server):
        self._server = server
        server.add_event_listener('start', self.__server_start)
        server.add_event_listener('stop', self.__server_stop)

    async def __server_start(self):
        self._reader, self._writer = await serial_asyncio.open_serial_connection(**self._kwargs)
        asyncio.ensure_future(self._read_requests())

    async def _read_requests(self):
        while not self._writer.is_closing():
            data = await self._reader.readuntil(b'\x00')
            data = data.decode()
            req = SerialRequest(self, data)
            asyncio.ensure_future(self._server.dispatch_event('request', req))

    async def __server_stop(self):
        self._writer.close()

    async def send(self, data: dict):
        data = '\n' + json.dumps(data) + '\n'
        self._writer.write(data.encode())


protocol_factory = SerialProtocol
