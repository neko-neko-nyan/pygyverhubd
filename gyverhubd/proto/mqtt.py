import asyncio
import json
import os
import sys
import typing

import aiomqtt

from . import Protocol, Request

__all__ = ["MqttProtocol"]


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
    def __init__(self, host: str, port=1883, **kwargs):
        self._host = host
        self._port = port
        self._client_kwargs = kwargs

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
        self._client = aiomqtt.Client(self._host, self._port, **self._client_kwargs)
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
