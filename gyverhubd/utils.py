import binascii
import enum

__all__ = ["Module", "parse_url", "generate_did", "response"]


class Module(enum.IntFlag):
    INFO = 1 << 0
    FSBR = 1 << 1
    FORMAT = 1 << 2

    DOWNLOAD = 1 << 3
    UPLOAD = 1 << 4

    OTA = 1 << 5
    OTA_URL = 1 << 6

    REBOOT = 1 << 7

    SET = 1 << 8
    READ = 1 << 9

    DELETE = 1 << 10
    RENAME = 1 << 11

    SERIAL = 1 << 12
    BT = 1 << 13
    WS = 1 << 14
    MQTT = 1 << 15


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


def generate_did(device: type):
    name = f"{device.__module__}/{device.__name__}"
    crc = binascii.crc32(name.encode('utf-8'))
    return hex(crc)[2:]


def response(typ: str, **kwargs):
    kwargs['type'] = typ
    return kwargs
