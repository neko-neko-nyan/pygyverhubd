import dataclasses

from . import Filesystem, response, Builder

__version__ = "0.0.1"

_FS_COMMANDS = frozenset((
    "fsbr", "format", "rename", "delete",
    "fetch", "fetch_chunk",
    "upload", "upload_chunk"
))


@dataclasses.dataclass
class DeviceInfo:
    wifi_mode: str = "None"
    ssid: str = "-"
    local_ip: str = "0.0.0.0"
    ap_ip: str = "0.0.0.0"
    mac: str = "00:00:00:00:00:00"
    rssi: str = "-0 dBm"
    uptime: str = "00:00:00"
    free_heap: str = "0 b"
    free_pgm: str = "0 b"
    flash_size: str = "0 b"
    cpu_freq: str = "0.0 mHz"


class Device:
    name: str
    id: str
    prefix: str = "MyDevices"

    icon: str = ""
    pin: int = 0  # TODO
    version: str = "0.0.1"
    update_info: str = ""
    author: str | None = None
    enable_auto_update: bool = False
    info: DeviceInfo | None = None
    fs: Filesystem | None = None

    # Overridable

    async def on_focus(self):
        pass

    async def on_unfocus(self):
        pass

    async def on_cli(self, command: str):
        pass

    async def reboot(self):
        raise NotImplementedError()

    async def ota_update(self, part, url: str | None = None, data: bytes | None = None, check_only: bool = False):
        raise NotImplementedError()

    async def build_ui(self, ui):
        pass

    async def on_discover(self) -> dict:
        return dict(name=self.name, icon=self.icon, version=self.update_info, PIN=self.pin)

    async def on_ui_update(self):
        builder = Builder()
        await self.build_ui(builder)
        return response("ui", controls=builder._components)

    async def on_ui_event(self, name: str, value: str):
        builder = Builder(name, value)
        await self.build_ui(builder)

    async def on_request_info(self) -> dict:
        if self.info is None:
            return dict(info=[__version__, self.version])
        else:
            i = self.info
            return dict(info=[__version__, self.version, i.wifi_mode, i.ssid, i.local_ip, i.ap_ip, i.mac,
                              i.rssi, i.uptime, i.free_heap, i.free_pgm, i.flash_size, i.cpu_freq])

    # API

    async def send(self, typ, **data):
        await self.server.send(typ, **data)

    async def broadcast(self, typ, **data):
        await self.server.broadcast(typ, **data)

    async def send_push(self, text: str, *, broadcast=False):
        if broadcast:
            await self.broadcast("push", text=text)
        else:
            await self.send("push", text=text)

    async def send_notice(self, text: str, color: int, *, broadcast=False):
        if broadcast:
            await self.broadcast("notice", text=text, color=color)
        else:
            await self.send("notice", text=text, color=color)

    async def send_alert(self, text: str, *, broadcast=False):
        if broadcast:
            await self.broadcast("alert", text=text)
        else:
            await self.send("alert", text=text)

    async def send_update(self, name: str, value: str, *, broadcast=False):
        if broadcast:
            await self.broadcast("update", updates={name: value})
        else:
            await self.send("update", updates={name: value})

    # internal

    def __init__(self, server):
        self.server = server
        self._ota_data = self._ota_name = None

    async def on_message(self, req, cmd: str, name: str | None):
        if cmd == "ping":
            await req.respond(response("OK"))
            return

        # # UI # #

        if cmd == "focus":
            req.set_focused(True)
            await self.on_focus()
            await req.respond(await self.on_ui_update())
            return

        if cmd == "unfocus":
            req.set_focused(False)
            await self.on_unfocus()
            return

        if cmd == "set":
            await self.on_ui_event(name, req.value)
            await req.respond(await self.on_ui_update())
            return

        # # INFO # #

        if cmd == "info":
            info = await self.on_request_info()
            await req.respond(response("info", **info))
            return

        if cmd == "reboot":
            await self.reboot()
            await req.respond(response("OK"))
            return

        if cmd == "cli":
            await self.on_cli(req.value)
            await req.respond(response("OK"))
            return

        # # FILESYSTEM # #

        if cmd in _FS_COMMANDS:
            if self.fs is None:
                return response("fs_error")

            return await self.fs.on_message(req, cmd, name)

        # # OTA # #

        if cmd == "ota_url":
            try:
                await self.ota_update(name, url=req.value)
            except Exception:
                await req.respond(response("ota_url_err"))
            else:
                await req.respond(response("ota_url_ok"))
            return

        if cmd == "ota":
            try:
                await self.ota_update(name, check_only=True)
            except Exception:
                await req.respond(response("ota_err"))
            else:
                self._ota_name = name
                self._ota_data = []
                await req.respond(response("ota_start"))
            return

        if cmd == "ota_chunk":
            if self._ota_data is None:
                await req.respond(response("ota_err"))
                return

            self._ota_data.append(req.value)

            if name == 'next':
                await req.respond(response("ota_next_chunk"))
                return

            try:
                await self.ota_update(self._ota_name, data=b''.join(self._ota_data))
            except Exception:
                await req.respond(response("ota_err"))
            else:
                self._ota_name = self._ota_data = None
                await req.respond(response("ota_end"))
            return
