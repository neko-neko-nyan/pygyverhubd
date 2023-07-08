import asyncio
import typing

from . import Device, Protocol, Request, response, GyverHubError, EventTarget, context, load_protocol

__all__ = ["Server", "run_server_async", "run_server"]


class Server(EventTarget):
    def __init__(self, *devices: Device, protocols: typing.List[typing.Union[Protocol, dict]] = ()):
        super().__init__()
        self._protocols: typing.List[Protocol] = []
        self.devices = devices
        self._running: typing.Optional[asyncio.Future] = None
        self.add_event_listener('request', self._on_request)
        self.add_event_listener('request.upload', self._on_request_upload)
        self.add_event_listener('request.ota', self._on_request_ota)

        for i in protocols:
            self.add_protocol(i)

    def add_protocol(self, proto: typing.Union[Protocol, dict]):
        if isinstance(proto, dict):
            name = proto.pop('name')
            proto = load_protocol(name, proto)

        self._protocols.append(proto)
        proto.bind(self)

    async def start(self):
        with context.server_context(self):
            await self.dispatch_event('start')

    async def stop(self):
        if self._running is not None:
            self._running.set_result(None)
            return

        with context.server_context(self):
            await self.dispatch_event('stop')

    async def _on_request(self, req: Request):
        with context.request_context(req), context.server_context(self):
            if req.cmd is None and req.did is None:
                for dev in self.devices:
                    with context.device_context(dev):
                        await dev.dispatch_event('discover')

                return

            for dev in self.devices:
                if dev.prefix != req.prefix or dev.id != req.did:
                    continue

                with context.device_context(dev):
                    if req.cmd is None:
                        await dev.dispatch_event('discover')
                    else:
                        try:
                            await dev.dispatch_event('request')
                        except GyverHubError as e:
                            await req.respond(response(e.type, text=e.message))

                break

    async def _on_request_upload(self, name: str, data: bytes):
        print(name, data)
        dev = self.devices[0]
        with context.server_context(self), context.device_context(dev):
            if dev.fs is not None:
                dev.fs.put_contents(name, data)

    async def _on_request_ota(self, part: str, data: bytes):
        dev = self.devices[0]
        with context.server_context(self), context.device_context(dev):
            if part not in dev.ota_parts:
                return
            await dev.ota_update(part, data)

    async def send(self, data, broadcast=False):
        for i in self._protocols:
            if broadcast or i.focused:
                await i.send(data)

    async def run(self):
        if self._running is not None:
            raise RuntimeError("Server is already running")

        self._running = asyncio.Future()
        await self.start()
        try:
            await self._running
        except asyncio.CancelledError:
            pass
        finally:
            self._running = None
            await self.stop()


async def run_server_async(*args, **kwargs):
    server = Server(*args, **kwargs)
    await server.run()


def run_server(*args, **kwargs):
    asyncio.run(run_server_async(*args, **kwargs))
