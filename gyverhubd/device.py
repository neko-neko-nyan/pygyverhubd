import dataclasses


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
    def __init__(self, prefix: str = "MyDevices", name: str = "", icon: str = "", did: int | None = None):
        self._prefix = prefix
        self._name = name
        self._icon = icon
        self._id = _generate_did() if did is None else str(did)

        self.version: str | None = "0.0.1"
        self.pin: int = 0
        self.atomic_updates: bool = True
        self.info: DeviceInfo | None = None
        self.fs: Filesystem | None = None
        self.ui = None

    @property
    def id(self):
        return self._id

    @property
    def icon(self):
        return self._icon

    @property
    def name(self):
        return self._name

    @property
    def prefix(self):
        return self._prefix

    def on_focus(self):
        pass

    def on_unfocus(self):
        pass

    def handle_cli(self, command: str):
        pass

    def reboot(self):
        raise NotImplementedError()

    def ota_update(self, part, url: str | None = None, data: bytes | None = None, check_only: bool = False):
        raise NotImplementedError()


def _generate_did():
    raise ValueError("Missing did and generating not supported!")
