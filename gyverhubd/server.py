import asyncio
import json

from . import Device, Protocol, Request, parse_url


class Server:
    def __init__(self, device: type[Device], *, protocols: list[Protocol] = ()):
        self._protocols: list[Protocol] = []
        self.device = device(self)

        for i in protocols:
            self.add_protocol(i)

    def add_protocol(self, proto: Protocol):
        self._protocols.append(proto)
        proto.set_handler_message(self._on_message)

    async def start(self):
        for i in self._protocols:
            await i.start()

    async def stop(self):
        for i in self._protocols:
            await i.stop()

    def _on_message(self, req: Request):
        asyncio.ensure_future(self._on_message_async(req))

    async def _on_message_async(self, req: Request):
        prefix, clid, did, cmd, name = parse_url(req.url)

        if self.device.prefix != prefix:
            return

        print(f">>> {cmd!r} {name!r}={req.value!r}")

        dev = self.device
        if cmd is None and (did is None or dev.id == did):
            res = dict(type="discover", name=dev.name, icon=dev.icon, version=dev.update_info, PIN=dev.pin)

        elif cmd is None or did != dev.id:
            return

        else:
            res = await dev.on_message(req, cmd, name)

        if res is not None:
            res.setdefault('id', dev.id)
            res = '\n' + json.dumps(res) + '\n'
            asyncio.ensure_future(req.respond(res))

    async def send(self, typ, **data):
        print(f"<<< {typ} {data}")
        data['type'] = typ
        data['id'] = self.device.id
        data = '\n' + json.dumps(data) + '\n'

        for i in self._protocols:
            if i.focused:
                await i.send(data)

    async def broadcast(self, typ, **data):
        print(f"<<< {typ} {data}")
        data['type'] = typ
        data['id'] = self.device.id
        data = '\n' + json.dumps(data) + '\n'

        for i in self._protocols:
            await i.send(data)


async def run_server_async(*args, **kwargs):
    server = Server(*args, **kwargs)
    await server.start()
    try:
        await asyncio.Future()
    finally:
        await server.stop()


def run_server(*args, **kwargs):
    asyncio.run(run_server_async(*args, **kwargs))
