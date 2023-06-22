import asyncio
import json

from gyverhubd.device import Device
from gyverhubd.proto.proto import Protocol, Request


def parse_url(url: str) -> tuple[str, str | None, str | None, str | None, str | None]:
    prefix, *url = url.split('/', maxsplit=4)
    cmd = clid = did = name = None

    if url:
        did, *url = url
    if len(url) == 1:
        print(prefix, url)
        raise ValueError("Invalid data!")
        # return prefix, clid, did, cmd, name
    if url:
        clid, cmd, *url = url
    if url:
        name, = url
    return prefix, clid, did, cmd, name


class Server:
    def __init__(self, device: Device, *, protocols: list[Protocol] = ()):
        self.device = device
        self._protocols: list[Protocol] = []

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
        prefix, clid, did, cmd, name = parse_url(req.url)

        if self.device.prefix != prefix:
            return

        print(f">>> {cmd!r} {name!r}={req.value!r}")

        dev = self.device
        if cmd is None and (did is None or dev.id == did):
            res = dev.response("discover", name=dev.name, icon=dev.icon, version=dev.version, PIN=dev.pin)

        elif cmd is None or did != dev.id:
            return

        else:
            res = dev.on_message(cmd, name, req.value)

        if res is not None:
            res = '\n' + json.dumps(res) + '\n'
            asyncio.ensure_future(req.respond(res))

    async def send(self, typ, **data):
        print(f"<<< {typ} {data}")
        data['type'] = typ
        data['id'] = self.device.id
        data = '\n' + json.dumps(data) + '\n'

        for i in self._protocols:
            await i.send(data)

    async def send_push(self, text: str):
        await self.send("push", text=text)

    async def send_notice(self, text: str, color: int):
        await self.send("notice", text=text, color=color)

    async def send_alert(self, text: str):
        await self.send("alert", text=text)

    async def send_update(self, name: str, value: str):
        await self.send("update", updates={name: value})


async def run_server_async(*args, **kwargs):
    server = Server(*args, **kwargs)
    await server.start()
    try:
        await asyncio.Future()
    finally:
        await server.stop()


def run_server(*args, **kwargs):
    asyncio.run(run_server_async(*args, **kwargs))
