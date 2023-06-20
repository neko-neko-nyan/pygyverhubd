import asyncio

__version__ = "0.0.1"

from gyverhubd.device import Device
from gyverhubd.proto.proto import Protocol


class Connection:
    def __init__(self, server: 'Server', client: tuple[str, int]):
        self._server = server
        self._client = client
        self._clid = None
        self._msgq = asyncio.Queue()

        print("+++", self._client)

    async def got_data(self, data):
        group = data[0]
        clid = did = name = value = None
        cmd = 'discover'

        if len(data) >= 3:
            did = data[1]
            clid = data[2]

            if len(data) >= 4:
                cmd = data[3]

                if len(data) == 5:
                    name, _, value = data[4].partition('/')

        if self._clid is None:
            self._clid = clid

        dev = self._server.device
        print(">>>",  cmd, name, value)

        if cmd == "discover":
            if self._server.device.prefix == group and (did is None or dev.id == did):
                await self.send("discover", version=dev.version)

        elif cmd == "ping":
            await self.send("OK")

        # # UI # #

        elif cmd == "focus":
            await self._rebuild_ui(dev)
            dev.on_focus()

        elif cmd == "unfocus":
            dev.on_unfocus()

        elif cmd == "set":
            if dev.ui is None:
                await self.send("OK")
            else:
                await self._rebuild_ui(dev, "set", name, value)

        elif cmd == "click":
            if dev.ui is None:
                await self.send("OK")
            else:
                await self._rebuild_ui(dev, "click", name, value)

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
            dev.handle_cli(value)
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

    async def _rebuild_ui(self, dev, action=None, component=None, value=None):
        await self.send("ui", controls=[{"type": "button", "name": "button1", "label": "Button 1", "size": 14}])

    async def _send_fsbr(self, dev):
        await self.send("fsbr", total=dev.fs.size, used=dev.fs.used, gzip=dev.atomic_updates, fs=dev.fs.get_files_info())

    async def send_push(self, text: str):
        await self.send("push", text=text)

    async def send_notice(self, text: str, color: int):
        await self.send("notice", text=text, color=color)

    async def send_alert(self, text: str):
        await self.send("alert", text=text)

    async def send_update(self, name: str, value: str):
        await self.send("update", updates={name: value})

    async def send(self, typ, **data):
        data['type'] = typ
        data['id'] = self._server.device.id
        await self._msgq.put(data)

    def disconnected(self, code):
        print("---", self._client, code)
        pass

    async def get_message(self):
        res = await self._msgq.get()
        print("<<<", res)
        return res


class Server:
    def __init__(self, device: Device):
        self.device = device
        self._protocols = []

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
