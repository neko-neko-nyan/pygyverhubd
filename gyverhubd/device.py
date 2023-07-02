from functools import cached_property

from . import Filesystem, response, DeviceUi, Module, DeviceInfo, __version__, generate_did

_FS_COMMANDS = frozenset((
    "fsbr", "format", "rename", "delete",
    "fetch", "fetch_chunk",
    "upload", "upload_chunk"
))


class Device:
    name: str
    id: str = None
    prefix: str = "MyDevices"

    icon: str = ""
    pin: int = 0  # TODO
    version: str = "0.0.1"
    update_info: str = ""
    update_format: str = "bin"
    author: str | None = None
    enable_auto_update: bool = False
    info: DeviceInfo | None = None
    fs: Filesystem | None = None
    ui: DeviceUi | None = None

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

    async def on_discover(self) -> dict:
        return dict(name=self.name, icon=self.icon, version=self.update_info, PIN=self.pin, ota_t=self.update_format,
                    max_upl=0xFFFF_FFFF_FFFF_FFFF, modules=self._disabled_modules)

    # API

    async def send(self, typ, **data):
        data['id'] = self.id
        data['type'] = typ
        await self.server.send(data)

    async def broadcast(self, typ, **data):
        data['id'] = self.id
        data['type'] = typ
        await self.server.send(data, broadcast=True)

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
            value |= Module.OTA | Module.OTA_URL
        if self.ui is None:
            value |= Module.SET
        if self.fs is None:
            value |= Module.FSBR | Module.FORMAT | Module.RENAME | Module.DELETE | Module.DOWNLOAD | Module.UPLOAD
        else:
            value |= self.fs.disabled_modules

        return value

    def __init__(self, server):
        self.server = server
        self._ota_data = self._ota_name = None
        if self.id is None:
            self.id = generate_did(type(self))

    async def on_message(self, req, cmd: str, name: str | None):
        if cmd == "ping":
            await req.respond(response("OK"))
            return

        # # UI # #

        if cmd == "focus":
            req.set_focused(True)
            await self.on_focus()
            if self.ui is None:
                await req.respond(response("ui", controls=[]))
            else:
                await req.respond(await self.ui.on_update())
            return

        if cmd == "unfocus":
            req.set_focused(False)
            await self.on_unfocus()
            return

        if cmd == "set":
            if self.ui is None:
                await req.respond(response("OK"))
            else:
                await req.respond(await self.ui.on_ui_event(name, req.value))
            return

        # # INFO # #

        if cmd == "info":
            if self.info is None:
                info = dict(versions=dict())
            else:
                info = self.info.to_json()

            info = dict(info)
            info['version'] = dict(info.get('version', {}))
            info['version']['Library'] = __version__
            if self.version:
                info['version'].setdefault('Firmware', self.version)

            await req.respond(response("info", info=info))
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
                await req.respond(response("fs_error"))
            else:
                await req.respond(await self.fs.on_message(req, cmd, name))
            return

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
