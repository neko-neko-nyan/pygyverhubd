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

    async def on_message(self, req, cmd: str, name: str | None) -> dict | None:
        if cmd == "ping":
            return response("OK")

        # # UI # #

        if cmd == "focus":
            req.set_focused(True)
            await self.on_focus()
            return await self._rebuild_ui()

        if cmd == "unfocus":
            req.set_focused(False)
            await self.on_unfocus()
            return

        if cmd == "set":
            return await self._rebuild_ui(name, req.value)

        # # INFO # #

        if cmd == "info":
            if self.info is None:
                return response("info", info=[__version__, self.version])
            else:
                i = self.info
                return response("info", info=[__version__, self.version, i.wifi_mode, i.ssid, i.local_ip, i.ap_ip,
                                              i.mac, i.rssi, i.uptime, i.free_heap, i.free_pgm, i.flash_size,
                                              i.cpu_freq])

        if cmd == "reboot":
            await self.reboot()
            return response("OK")

        if cmd == "cli":
            await self.on_cli(req.value)
            return response("OK")

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
                return response("ERR")
            else:
                return response("OK")

        if cmd == "ota":
            try:
                await self.ota_update(name, check_only=True)
            except Exception:
                return response("ota_err")
            else:
                self._ota_name = name
                self._ota_data = []
                return response("ota_start")

        if cmd == "ota_chunk":
            if self._ota_data is None:
                return response("ota_err")

            self._ota_data.append(req.value)

            if name == 'next':
                return response("ota_next_chunk")

            elif name == 'last':
                try:
                    await self.ota_update(self._ota_name, data=b''.join(self._ota_data))
                except Exception:
                    return response("ota_err")
                else:
                    self._ota_name = self._ota_data = None
                    return response("ota_end")

    async def _rebuild_ui(self, component=None, value=None):
        if component is not None:
            builder = Builder(component, value)
            await self.build_ui(builder)

        builder = Builder()
        await self.build_ui(builder)
        return response("ui", controls=builder._components)
