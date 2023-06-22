import asyncio

from gyverhubd.device import Device
from gyverhubd.proto.proto import Protocol


__version__ = "0.0.1"


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


class Connection:
    def __init__(self, server: 'Server', client: tuple[str, int]):
        self._server = server
        self._client = client
        self._clid = None
        self._msgq = asyncio.Queue()

        print(f"+++ {client[0]}:{client[1]}")

    async def got_data(self, url, value):
        prefix, clid, did, cmd, name = parse_url(url)

        if self._clid is None:
            self._clid = clid

        if self._server.device.prefix != prefix:
            return

        dev = self._server.device

        print(f">>> {cmd!r} {name!r}={value!r} ({clid!r} -> {did!r})")

        if cmd is None and (did is None or dev.id == did):
            await self.send("discover", name=dev.name, icon=dev.icon, version=dev.version, PIN=dev.pin)

        if cmd is None or did != dev.id:
            return

        if cmd == "ping":
            await self.send("OK")

        # # UI # #

        elif cmd == "focus":
            await self._rebuild_ui(dev)
            dev.on_focus()

        elif cmd == "unfocus":
            dev.on_unfocus()

        elif cmd == "set":
            await self._rebuild_ui(dev, name, value)

        # # INFO # #

        elif cmd == "info":
            if dev.info is None:
                await self.send("info", info=[__version__, dev.version])
            else:
                i = dev.info
                await self.send("info", info=[__version__, dev.version, i.wifi_mode, i.ssid, i.local_ip, i.ap_ip, i.mac,
                                              i.rssi, i.uptime, i.free_heap, i.free_pgm, i.flash_size, i.cpu_freq])

        elif cmd == "reboot":
            dev.reboot()
            await self.send("OK")

        elif cmd == "cli":
            dev.on_cli(value)
            await self.send("OK")

        # # FILESYSTEM # #

        elif cmd == "fsbr":
            # not mounted = fs_error
            await self._send_fsbr(dev)

        elif cmd == "format":
            try:
                dev.fs.format()
            except Exception:
                await self.send("ERR")
            else:
                await self.send("OK")

        elif cmd == "rename":
            try:
                dev.fs.rename(name, value)
            except Exception:
                await self.send("ERR")
            else:
                await self._send_fsbr(dev)

        elif cmd == "delete":
            try:
                dev.fs.delete(name)
            except Exception:
                await self.send("ERR")
            else:
                await self._send_fsbr(dev)

        elif cmd == "fetch":
            try:
                self._fetch_temp = dev.fs.get_contents(name)
            except Exception:
                await self.send("fetch_err")
            else:
                await self.send("fetch_start")

        elif cmd == "fetch_chunk":
            if self._fetch_temp is None:
                await self.send("fetch_err")
            else:
                await self.send("fetch_next_chunk", chunk=0, amount=1, data=self._fetch_temp)
                self._fetch_temp = None

        elif cmd == "upload":
            try:
                dev.fs.put_contents(name, b'')
            except Exception:
                await self.send("upload_err")
            else:
                self._upload_name = name
                self._upload_data = []
                await self.send("upload_start")

        elif cmd == "upload_chunk":
            if self._upload_data is None:
                await self.send("upload_err")
            else:
                self._upload_data.append(value)

                if name == 'next':
                    await self.send("upload_next_chunk")

                elif name == 'last':
                    try:
                        dev.fs.put_contents(self._upload_name, b''.join(self._upload_data))
                    except Exception:
                        await self.send("upload_err")
                    else:
                        self._upload_name = self._upload_data = None
                        await self.send("upload_end")

        # # OTA # #

        elif cmd == "ota_url":
            try:
                dev.ota_update(name, url=value)
            except Exception:
                await self.send("ERR")
            else:
                await self.send("OK")

        elif cmd == "ota":
            try:
                dev.ota_update(name, check_only=True)
            except Exception:
                await self.send("ota_err")
            else:
                self._ota_name = name
                self._ota_data = []
                await self.send("ota_start")

        elif cmd == "ota_chunk":
            if self._ota_data is None:
                await self.send("ota_err")
            else:
                self._ota_data.append(value)

                if name == 'next':
                    await self.send("ota_next_chunk")

                elif name == 'last':
                    try:
                        dev.ota_update(self._ota_name, data=b''.join(self._ota_data))
                    except Exception:
                        await self.send("ota_err")
                    else:
                        self._ota_name = self._ota_data = None
                        await self.send("ota_end")

    async def _rebuild_ui(self, dev, component=None, value=None):
        await self.send("ui", controls=[{"type": "button", "name": "button1", "label": "Button 1", "size": 14}])

    async def _send_fsbr(self, dev):
        await self.send("fsbr", total=dev.fs.size, used=dev.fs.used, gzip=dev.update_format == "gzip",
                        fs=dev.fs.get_files_info())

    async def send_push(self, text: str):
        await self.send("push", text=text)

    async def send_notice(self, text: str, color: int):
        await self.send("notice", text=text, color=color)

    async def send_alert(self, text: str):
        await self.send("alert", text=text)

    async def send_update(self, name: str, value: str):
        await self.send("update", updates={name: value})

    async def send(self, typ, **data):
        print(f"<<< {typ} {data}")
        data['type'] = typ
        data['id'] = self._server.device.id
        await self._msgq.put(data)

    def disconnected(self, code):
        print(f"--- {self._client[0]}:{self._client[1]} ({code})")

    async def get_message(self):
        return await self._msgq.get()


class Server:
    def __init__(self, device: Device, *, protocols: list[Protocol] = ()):
        self.device = device
        self._protocols = []

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

    def connected(self, client: tuple[str, int]) -> Connection:
        return Connection(self, client)


async def run_server_async(*args, **kwargs):
    server = Server(*args, **kwargs)
    await server.start()
    try:
        await asyncio.Future()
    finally:
        await server.stop()


def run_server(*args, **kwargs):
    asyncio.run(run_server_async(*args, **kwargs))
