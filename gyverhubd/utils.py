import binascii
import contextlib
import enum
import importlib
import shutil
import typing

from Crypto.Hash import SHA3_256

__all__ = ["Module", "parse_url", "generate_did", "response", "rmtree_exc", "hash_file", "load_protocol"]


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


def parse_url(url: str) -> \
        typing.Tuple[str, typing.Optional[str], typing.Optional[str], typing.Optional[str], typing.Optional[str]]:
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


def rmtree_exc(path):
    errors = []

    def _onerror(_, __, exc_info):
        _, value, _ = exc_info
        errors.append(value)

    shutil.rmtree(path, onerror=_onerror)
    if errors:
        raise errors[0]


def hash_file(path: typing.Union[str, typing.IO[bytes]]):
    hasher = SHA3_256.new()

    if isinstance(path, str):
        fp = open(path, 'rb')
    else:
        fp = contextlib.nullcontext(path)

    with fp as f:
        while True:
            data = f.read(1 * 1024 * 1024)
            if not data:
                break

            hasher.update(data)

    return hasher.digest()


def load_protocol(name, options: typing.Optional[dict] = None):
    if options is None:
        options = {}

    mod = importlib.import_module(f".proto.{name}", __package__)
    return mod.protocol_factory(**options)
