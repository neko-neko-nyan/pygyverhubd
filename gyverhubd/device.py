import dataclasses


__version__ = "0.0.1"


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


class Filesystem:
    size: int
    used: int

    def get_files_info(self) -> dict[str, int]:
        pass

    def format(self):
        pass

    def delete(self, path: str):
        pass

    def rename(self, path: str, new_path: str):
        pass

    def get_contents(self, path: str) -> bytes:
        pass

    def put_contents(self, path: str, data: bytes):
        pass


class Device:
    name: str
    id: str
    prefix: str = "MyDevices"

    icon: str = ""
    pin: int = 0  # TODO
    version: str = ""
    author: str | None = None
    enable_auto_update: bool = False
    info: DeviceInfo | None = None
    update_format: str | None = None
    fs: Filesystem | None = None

    # Overridable

    def on_focus(self):
        pass

    def on_unfocus(self):
        pass

    def on_cli(self, command: str):
        pass

    def reboot(self):
        raise NotImplementedError()

    def ota_update(self, part, url: str | None = None, data: bytes | None = None, check_only: bool = False):
        raise NotImplementedError()

    def build_ui(self, ui):
        pass

    # API

    def response(self, typ: str, **kwargs):
        kwargs.setdefault("id", self.id)
        kwargs['type'] = typ
        return kwargs

    def __init__(self):
        self._fetch_temp = None
        self._upload_data = self._upload_name = None
        self._ota_data = self._ota_name = None

    def on_message(self, cmd: str, name: str | None, value: str | None) -> dict | None:
        if cmd == "ping":
            return self.response("OK")

        # # UI # #

        if cmd == "focus":
            self.on_focus()
            return self._rebuild_ui()

        if cmd == "unfocus":
            self.on_unfocus()
            return

        if cmd == "set":
            return self._rebuild_ui(name, value)

        # # INFO # #

        if cmd == "info":
            if self.info is None:
                return self.response("info", info=[__version__, self.version])
            else:
                i = self.info
                return self.response("info", info=[__version__, self.version, i.wifi_mode, i.ssid, i.local_ip, i.ap_ip,
                                                   i.mac, i.rssi, i.uptime, i.free_heap, i.free_pgm, i.flash_size,
                                                   i.cpu_freq])

        if cmd == "reboot":
            self.reboot()
            return self.response("OK")

        if cmd == "cli":
            self.on_cli(value)
            return self.response("OK")

        # # FILESYSTEM # #

        if cmd == "fsbr":
            # not mounted = fs_error
            return self._send_fsbr()

        if cmd == "format":
            try:
                self.fs.format()
            except Exception:
                return self.response("ERR")
            else:
                return self.response("OK")

        if cmd == "rename":
            try:
                self.fs.rename(name, value)
            except Exception:
                return self.response("ERR")
            else:
                return self._send_fsbr()

        if cmd == "delete":
            try:
                self.fs.delete(name)
            except Exception:
                return self.response("ERR")
            else:
                return self._send_fsbr()

        if cmd == "fetch":
            try:
                self._fetch_temp = self.fs.get_contents(name)
            except Exception:
                return self.response("fetch_err")
            else:
                return self.response("fetch_start")

        if cmd == "fetch_chunk":
            if self._fetch_temp is None:
                return self.response("fetch_err")

            self._fetch_temp = None
            return self.response("fetch_next_chunk", chunk=0, amount=1, data=self._fetch_temp)

        if cmd == "upload":
            try:
                self.fs.put_contents(name, b'')
            except Exception:
                return self.response("upload_err")
            else:
                self._upload_name = name
                self._upload_data = []
                return self.response("upload_start")

        if cmd == "upload_chunk":
            if self._upload_data is None:
                return self.response("upload_err")

            self._upload_data.append(value)

            if name == 'next':
                return self.response("upload_next_chunk")

            elif name == 'last':
                try:
                    self.fs.put_contents(self._upload_name, b''.join(self._upload_data))
                except Exception:
                    return self.response("upload_err")
                else:
                    self._upload_name = self._upload_data = None
                    return self.response("upload_end")

        # # OTA # #

        if cmd == "ota_url":
            try:
                self.ota_update(name, url=value)
            except Exception:
                return self.response("ERR")
            else:
                return self.response("OK")

        if cmd == "ota":
            try:
                self.ota_update(name, check_only=True)
            except Exception:
                return self.response("ota_err")
            else:
                self._ota_name = name
                self._ota_data = []
                return self.response("ota_start")

        if cmd == "ota_chunk":
            if self._ota_data is None:
                return self.response("ota_err")

            self._ota_data.append(value)

            if name == 'next':
                return self.response("ota_next_chunk")

            elif name == 'last':
                try:
                    self.ota_update(self._ota_name, data=b''.join(self._ota_data))
                except Exception:
                    return self.response("ota_err")
                else:
                    self._ota_name = self._ota_data = None
                    return self.response("ota_end")

    def _rebuild_ui(self, component=None, value=None):
        return self.response("ui", controls=[{"type": "button", "name": "button1", "label": "Button 1", "size": 14}])

    def _send_fsbr(self):
        if self.fs is None:
            return self.response("fs_error")

        return self.response("fsbr", total=self.fs.size, used=self.fs.used, gzip=self.update_format == "gzip",
                             fs=self.fs.get_files_info())


def _generate_did():
    raise ValueError("Missing did and generating not supported!")
