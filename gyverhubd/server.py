import asyncio

from . import Device, Protocol, Request, response, GyverHubError

__all__ = ["Server", "run_server_async", "run_server"]


class Server:
    def __init__(self, *devices: type[Device], protocols: list[Protocol] = ()):
        self._protocols: list[Protocol] = []
        self.devices = [device(self) for device in devices]

        for i in protocols:
            self.add_protocol(i)

    def add_protocol(self, proto: Protocol):
        self._protocols.append(proto)
        proto.bind(self)

    async def start(self):
        for i in self._protocols:
            await i.start()

    async def stop(self):
        for i in self._protocols:
            await i.stop()

    async def handle_request(self, req: Request):
        if req.cmd is None and req.did is None:
            for dev in self.devices:
                data = await dev.on_discover()
                if data is not None:
                    data['type'] = 'discover'
                    data['id'] = dev.id
                    await req.respond(data)
            return

        for dev in self.devices:
            if dev.prefix != req.prefix or dev.id != req.did:
                continue

            if req.cmd is None:
                data = await dev.on_discover()
                if data is not None:
                    data['type'] = 'discover'
                    data['id'] = dev.id
                    await req.respond(data)
            else:
                try:
                    await dev.on_message(req, req.cmd, req.name)
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
