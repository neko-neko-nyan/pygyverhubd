import io
import os
import sys
import typing
import zipfile

import aiohttp
from Crypto.Hash import SHA3_256
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS

from gyverhubd import context, Server, hash_file

__all__ = ['download_and_update', 'restart_app']


async def download_and_update(dev, part: str, url: str):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            resp.raise_for_status()
            data = await resp.read()

    await dev.ota_update(part, data)


async def restart_app(_):
    server: Server = context.server
    os.environ['__SRV_AUTO_RESTART'] = '1'
    await server.stop()


async def install_update(dev, part: str, data: bytes):
    if part != 'flash':
        raise ValueError("You can only update flash")

    typ = type(dev)
    mod_name = typ.__module__
    mod = sys.modules[mod_name]
    loader = mod.__loader__

    try:
        key = loader.get_data('PKEY')
    except OSError:
        key = None

    if key is not None:
        with io.BytesIO(data) as fp:
            validate_package(fp, key)

    with open(loader.archive + '.tmp', 'wb') as f:
        f.write(data)

    server: Server = context.server
    os.environ['__SRV_AUTO_RESTART'] = '1'
    os.environ['__SRV_OTA'] = '1'
    await server.stop()


def validate_package(pkg_path: typing.IO[bytes], key: bytes):
    with zipfile.ZipFile(pkg_path) as zf:
        file_hashes = []

        for zi in zf.filelist:
            if zi.is_dir() or zi.filename == 'SIGN':
                continue

            with zf.open(zi) as f:
                file_hash = hash_file(f)

            file_hashes.append((zi.filename, file_hash))

        signature = zf.read('SIGN')

    file_hashes.sort(key=lambda x: x[0])

    hasher = SHA3_256.new()
    for name, data_hash in file_hashes:
        hasher.update(SHA3_256.new(name.encode('utf-8')).digest())
        hasher.update(data_hash)

    key = DSA.import_key(key)
    signer = DSS.new(key, 'fips-186-3')
    signer.verify(hasher, signature)
