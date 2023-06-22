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


def _generate_did():
    raise ValueError("Missing did and generating not supported!")
