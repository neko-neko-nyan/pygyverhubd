import asyncio
import json
import os
import ssl
import sys
import typing
import socket

import aiomqtt

from . import Protocol, Request

__all__ = ["MqttProtocol", "protocol_factory"]

_HELP = """\
List of MQTT protocol options:
username       str   The username to authenticate with.
password       str   The password to authenticate with.
client-id      str   The client ID to use. If not set, one will be generated automatically.
protocol       str   The version of the MQTT protocol. Must be one of: V31, V311, V5.
clean-session  bool  If true, the broker will remove all information about this client when it disconnects. If false,
                     the client is a persistent client and subscription information and queued messages will be retained
                     when the client disconnects.
transport      str   The transport protocol to use. Either "tcp" or "websockets".
timeout        float The default timeout for all communication with the broker in seconds.
keepalive      int   The keepalive timeout for the client in seconds.
bind-address   str   The IP address of a local network interface to bind this client to.
bind-port      int   The network port to bind this client to.
clean-start    bool  V5 only: Set the clean start flag always or never.
socket-options       Options to pass to the underlying socket. List of comma-separated items, in format LEVEL:NAME:VALUE
                     or LEVEL:NAME::LEN. Level and name are symbolic constants, without SOL_/SO_ prefixes.
websocket-path str   The path to use for websockets.
websocket-headers    The headers to use for websockets. List of comma-separated items, in format NAME:VALUE.
tls            true  Enable TLS/MQTTS connection to broker with system-default parameters.
tls                  Enable TLS/MQTTS connection to broker with specified parameters. List of comma-separated items,
                     in format NAME:VALUE. Name can be one of:
  ca_certs     str   PEM-encoded CA certificate to verify broker.
  certfile     str   PEM-encoded client certificate.
  keyfile      str   Private key file.
  keyfile_password str Password for private key.
  ciphers      str   Ciphers for secure connection. It should be a string in the OpenSSL cipher list format.
  tls_version  str   SSL/TLS version. Must be one of: SSLv2, SSLv3, TLSv1, TLSv1_1, TLSv1_2 or TLS (default).
"""


def _parse_sockopt(opt: str):
    level, name, *opt = opt.split(':')
    level = getattr(socket, f'SOL_{level.upper()}')
    name = getattr(socket.SO_BROADCAST, f'SO_{name.upper()}')

    if len(opt) == 2:
        value = None, int(opt[1])
    elif len(opt) == 1:
        if opt[0].isnumeric():
            value = int(opt[0]),
        else:
            value = opt[0].encode()
    else:
        raise ValueError(f"Invalid value for socket option: {opt}")

    return level, name, *value


def _parse_options(options: typing.Dict[str, str]) -> dict:
    if options is None:
        return {}

    res = {}
    for option, value in options.items():
        if option in {'keepalive', 'bind-port'}:
            res[option.replace('-', '_')] = int(value)

        elif option in {'bind-address', 'client-id', 'username', 'password', 'websocket-path', 'transport'}:
            res[option.replace('-', '_')] = value

        elif option == 'protocol':
            res['protocol'] = aiomqtt.ProtocolVersion[value]

        elif option == 'timeout':
            res['timeout'] = float(value)

        elif option in {'clean-session', 'clean-start'}:
            value = value.lower()
            if value in {'yes', 'on', 'true'}:
                res[option.replace('-', '_')] = True
            elif value in {'no', 'off', 'false'}:
                res[option.replace('-', '_')] = True
            else:
                raise ValueError(f"Invalid MQTT option ({option}) value: {value!r}")

        elif option == 'socket-options':
            res['socket_options'] = tuple((_parse_sockopt(i) for i in value.split(',')))

        elif option == 'websocket-headers':
            value = (i.partition(':') for i in value.split(','))
            res['websocket_headers'] = {k: v for k, _, v in value}

        elif option == 'tls':
            if value.lower() in {'yes', 'on', 'true'}:
                res['tls_params'] = aiomqtt.TLSParameters()
            else:
                value = (i.partition(':') for i in value.split(','))
                value = {k: v for k, _, v in value}
                if 'tls_version' in value:
                    value['tls_version'] = getattr(ssl, f'PROTOCOL_{value["tls_version"]}')
                res['tls_params'] = aiomqtt.TLSParameters(**value)

        elif option == 'help':
            print(_HELP, file=sys.stderr)
            sys.exit(0)

        else:
            raise ValueError(f"Invalid MQTT option {option!r}")

    return res


class MqttRequest(Request):
    def __init__(self, protocol, message: aiomqtt.Message):
        super().__init__(message.topic.value, message.payload.decode('ascii'))
        self.protocol: MqttProtocol = protocol

        if not self.value:
            self.value = None

        if self.cmd is None:
            self.clid = self.value
            self.value = None

    async def respond(self, data: dict):
        if self.did is not None:
            data['id'] = self.did
        data = '\n' + json.dumps(data) + '\n'
        await self.protocol.send_to(self, data)

    def set_focused(self, value: bool):
        pass


class MqttProtocol(Protocol):
    def __init__(self, host: str, options: typing.Dict[str, str] = None):
        host, _, port = host.rpartition(':')
        if host:
            port = int(port)
        else:
            host = port
            port = 1883

        self._client_kwargs = _parse_options(options)
        self._client_kwargs['hostname'] = host
        self._client_kwargs['port'] = port

        self._client: typing.Optional[aiomqtt.Client] = None
        self._server = None
        self._stopped = False
        self._prefixes = []

    @property
    def focused(self) -> bool:
        return False

    def bind(self, server):
        self._server = server
        self._prefixes.clear()
        server.add_event_listener('start', self.__server_start)
        server.add_event_listener('stop', self.__server_stop)

    async def __server_start(self):
        self._client = aiomqtt.Client(**self._client_kwargs)
        await self._client.connect()
        asyncio.ensure_future(self._messages())

        for dev in self._server.devices:
            await self._client.subscribe(dev.prefix)
            await self._client.subscribe(f"{dev.prefix}/{dev.id}/#")
            await self._client.publish(f"{dev.prefix}/hub/{dev.id}/status", b'online')
            self._prefixes.append(dev.prefix)

    async def _messages(self):
        async with self._client.messages() as messages:
            try:
                async for message in messages:
                    req = MqttRequest(self, message)
                    asyncio.ensure_future(self._server.dispatch_event('request', req))
            except aiomqtt.MqttError as e:
                if not self._stopped:
                    raise e

    async def __server_stop(self):
        for dev in self._server.devices:
            await self._client.publish(f"{dev.prefix}/hub/{dev.id}/status", b'offline')

        self._stopped = True
        await self._client.disconnect()

    async def send(self, data: dict):
        data = '\n' + json.dumps(data) + '\n'
        for prefix in self._prefixes:
            await self._client.publish(f"{prefix}/hub", data)

    async def send_to(self, req: MqttRequest, data: str):
        if req.did is None:
            await self._client.publish(f"{req.prefix}/hub", data)
        else:
            await self._client.publish(f"{req.prefix}/hub/{req.clid}/{req.did}", data)


protocol_factory = MqttProtocol

if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    # fix for aiomqtt
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
