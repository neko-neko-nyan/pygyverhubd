import binascii
import typing
from functools import cached_property

from . import Filesystem, response, DeviceUi, Module, DeviceInfo, __version__, generate_did, EventTarget, request, \
    server

__all__ = ["Device"]

_FS_COMMANDS = frozenset((
    "fsbr", "format", "rename", "delete",
    "fetch", "fetch_chunk",
    "upload", "upload_chunk"
))


class Device(EventTarget):
    name: str
    id: str = None
    prefix: str = "MyDevices"

    icon: str = ""
    pin: typing.Optional[int] = None
    version: str = "0.0.1"
    update_info: str = ""
    update_format: str = "bin"
    author: typing.Optional[str] = None
    enable_auto_update: bool = False
    info: typing.Optional[DeviceInfo] = None
    fs: typing.Optional[Filesystem] = None
    ui: typing.Optional[DeviceUi] = None
    ota_parts: tuple = ()  # may contain 'fs' or 'flash'

    # Overridable

    async def on_focus(self):
        pass

    async def on_unfocus(self):
        pass

    async def on_cli(self, command: str):
        pass

    async def reboot(self):
        raise NotImplementedError()

    async def ota_update(self, part: str, data: bytes):
        raise NotImplementedError()

    async def ota_url(self, part: str, url: str):
        raise NotImplementedError()

    async def on_discover(self) -> dict:
        h = 0
        if self.pin is not None:
            for c in f"{self.pin:0>4}":
                h = (h << 5) - h + ord(c)

        return dict(name=self.name, icon=self.icon, version=self.update_info, PIN=h, ota_t=self.update_format,
                    max_upl=0xFFFF_FFFF_FFFF_FFFF, modules=self._disabled_modules)

    # API

    async def send(self, typ, **data):
        data['id'] = self.id
        data['type'] = typ
        await server.send(data)

    async def broadcast(self, typ, **data):
        data['id'] = self.id
        data['type'] = typ
        await server.send(data, broadcast=True)

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

    @cached_property
    def _disabled_modules(self):
        value = 0
        if self.info is None:
            value |= Module.INFO
        if type(self).reboot == Device.reboot:  # not overrided
            value |= Module.REBOOT
        if type(self).ota_update == Device.ota_update:  # not overrided
            value |= Module.OTA
        if type(self).ota_url == Device.ota_url:  # not overrided
            value |= Module.OTA_URL
        if self.ui is None:
            value |= Module.SET
        if self.fs is None:
            value |= Module.FSBR | Module.FORMAT | Module.RENAME | Module.DELETE | Module.DOWNLOAD | Module.UPLOAD
        else:
            value |= self.fs.disabled_modules

        return value

    def __init__(self):
        super().__init__()
        self._ota_data = self._ota_name = None
        if self.id is None:
            self.id = generate_did(type(self))

        self.add_event_listener('discover', self._on_discover)
        self.add_event_listener('request', self._on_request)

    async def _on_discover(self):
        data = await self.on_discover()
        if data is not None:
            data['type'] = 'discover'
            data['id'] = self.id
            await request.respond(data)

    async def _on_request(self):
        cmd = request.cmd

        if cmd == "ping":
            await request.respond(response("OK"))
            return

        # # UI # #

        if cmd == "focus":
            request.set_focused(True)
            await self.on_focus()
            if self.ui is None:
                await request.respond(response("ui", controls=[]))
            else:
                await request.respond(await self.ui.on_update())
            return

        if cmd == "unfocus":
            request.set_focused(False)
            await self.on_unfocus()
            return

        if cmd == "set":
            if self.ui is None:
                await request.respond(response("OK"))
            else:
                await request.respond(await self.ui.on_ui_event(request.name, request.value))
            return

        # # INFO # #

        if cmd == "info":
            if self.info is None:
                info = dict(version=dict(Library=__version__, Firmware=self.version))
            else:
                info = self.info.to_json(self.version)
            await request.respond(response("info", info=info))
            return

        if cmd == "reboot":
            await self.reboot()
            await request.respond(response("OK"))
            return

        if cmd == "cli":
            await self.on_cli(request.value)
            await request.respond(response("OK"))
            return

        # # FILESYSTEM # #

        if cmd in _FS_COMMANDS:
            if self.fs is None:
                await request.respond(response("fs_error"))
            else:
                await request.respond(await self.fs.on_message())
            return

        # # OTA # #

        if cmd == "ota_url":
            if request.name not in self.ota_parts:
                await request.respond(response("ERR", text="Cant update this partition"))
                return

            try:
                await self.ota_url(request.name, url=request.value)
            except Exception:
                await request.respond(response("ota_url_err"))
            else:
                await request.respond(response("ota_url_ok"))
            return

        if cmd == "ota":
            if request.name not in self.ota_parts:
                await request.respond(response("ERR", text="Cant update this partition"))
                return

            self._ota_name = request.name
            self._ota_data = []
            await request.respond(response("ota_start"))
            return

        if cmd == "ota_chunk":
            if self._ota_data is None:
                await request.respond(response("ota_err"))
                return

            self._ota_data.append(binascii.a2b_base64(request.value))

            if request.name == 'next':
                await request.respond(response("ota_next_chunk"))
                return

            try:
                await self.ota_update(self._ota_name, b''.join(self._ota_data))
            except Exception:
                await request.respond(response("ota_err"))
            else:
                self._ota_name = self._ota_data = None
                await request.respond(response("ota_end"))
            return
