import asyncio
import json
import sys
import typing

import serial_asyncio

from . import Protocol, Request

__all__ = ["SerialProtocol", "protocol_factory"]

_HELP = """\
List of serial protocol options:
baudrate           int   Port communication speed, default is 9600.
config             str   Port configuration. Default is "8n1", 8 bits per byte, no parity checks, one stop bit.
xonxoff            bool  Enable software flow control.
rtscts             bool  Enable hardware (RTS/CTS) flow control.
dsrdtr             bool  Enable hardware (DSR/DTR) flow control.
exclusive          bool  Set exclusive access mode (POSIX only). A port cannot be opened in exclusive access mode if it
                         is already open in exclusive access mode.
timeout            float Read timeout value in seconds.
write_timeout      float Write timeout value in seconds.
inter_byte_timeout float Inter-character timeout. Disabled by default.
"""


def _parse_options(options: typing.Dict[str, str]) -> dict:
    if options is None:
        return {}

    res = {}
    for option, value in options.items():
        if option == 'baudrate':
            res['baudrate'] = int(value)

        elif option in {'timeout', 'write_timeout', 'inter_byte_timeout'}:
            res[option] = float(value)

        elif option in {'xonxoff', 'rtscts', 'dsrdtr', 'exclusive'}:
            value = value.lower()
            if value in {'yes', 'on', 'true'}:
                res[option] = True
            elif value in {'no', 'off', 'false'}:
                res[option] = True
            else:
                raise ValueError(f"Invalid serial option ({option}) value: {value!r}")

        elif option == 'config':
            res['bytesize'] = int(value[0])
            res['parity'] = value[1].upper()
            if len(value) == 3:
                res['stopbits'] = int(value[2:])
            else:
                res['stopbits'] = float(value[2:])

        elif option == 'help':
            print(_HELP, file=sys.stderr)
            sys.exit(0)

        else:
            raise ValueError(f"Invalid serial option {option!r}")

    return res


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
    def __init__(self, port: str, options: typing.Dict[str, str] = None):
        self._reader = self._writer = None
        self._kwargs = _parse_options(options)
        self._kwargs['url'] = port
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
