import asyncio

from . import Device, Protocol, Request, response, GyverHubError, EventTarget, context

__all__ = ["Server", "run_server_async", "run_server"]


class Server(EventTarget):
    def __init__(self, *devices: type[Device], protocols: list[Protocol] = ()):
        super().__init__()
        self._protocols: list[Protocol] = []
        self.devices = [device(self) for device in devices]
        self.add_event_listener('request', self._on_request)

        for i in protocols:
            self.add_protocol(i)

    def add_protocol(self, proto: Protocol):
        self._protocols.append(proto)
        proto.bind(self)

    async def start(self):
        with context.server_context(self):
            await self.dispatch_event('start')

    async def stop(self):
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

    async def send(self, data, broadcast=False):
        for i in self._protocols:
            if broadcast or i.focused:
                await i.send(data)


async def run_server_async(*args, **kwargs):
    server = Server(*args, **kwargs)
    await server.start()
    try:
        await asyncio.Future()
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        await server.stop()


def run_server(*args, **kwargs):
    asyncio.run(run_server_async(*args, **kwargs))
