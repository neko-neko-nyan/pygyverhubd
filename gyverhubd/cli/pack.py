import getpass
import os
import pathlib
import typing
import zipfile

from Crypto.Hash import SHA3_256
from Crypto.IO import PKCS8, PEM
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Util import asn1

from gyverhubd import hash_file


def import_private_key(key: str) -> DSA.DsaKey:
    der = PEM.decode(key, None)[0]
    try:
        oid, x, pub = PKCS8.unwrap(der)
    except ValueError:
        while True:
            passphrase = getpass.getpass("Password: ")
            try:
                oid, x, pub = PKCS8.unwrap(der, passphrase)
                break
            except ValueError:
                print("Invalid password")

    if oid != DSA.oid:
        raise ValueError("No PKCS#8 encoded DSA key")

    x = asn1.DerInteger().decode(x).value
    pub = asn1.DerSequence().decode(pub)
    p, q, g = list(pub)
    tup = (pow(g, x, p), g, p, q, x)
    return DSA.construct(tup)


def make_package(base_path: pathlib.Path, key: typing.Optional[DSA.DsaKey],
                 out_path: typing.Union[pathlib.Path, typing.IO[bytes]]):
    with zipfile.ZipFile(out_path, 'w') as zf:
        file_hashes = []

        for dir_path, dirs, files in os.walk(base_path):
            for i in tuple(dirs):
                if i.startswith('.'):
                    dirs.remove(i)

            for filename in files:
                if filename.startswith('.'):
                    continue

                file = os.path.join(dir_path, filename)
                filename = '/'.join(os.path.normpath(os.path.relpath(file, base_path)).split(os.path.sep))

                zf.write(file, filename)
                file_hashes.append((filename, hash_file(file)))

        if key is not None:
            pkey = key.public_key().export_key("DER")
            zf.writestr('PKEY', pkey)
            file_hashes.append(('PKEY', SHA3_256.new(pkey).digest()))

        file_hashes.sort(key=lambda x: x[0])

        hasher = SHA3_256.new()
        for name, data_hash in file_hashes:
            hasher.update(SHA3_256.new(name.encode('utf-8')).digest())
            hasher.update(data_hash)

        if key is not None:
            signer = DSS.new(key, 'fips-186-3')
            signature = signer.sign(hasher)
            zf.writestr('SIGN', signature)


def do_pack(args):
    output = args.output
    if output is None:
        output = args.directory.resolve()
        output = output.with_suffix(output.suffix + '.zip')

    key = None
    if args.sign is not None:
        key = import_private_key(args.sign.read())

    make_package(args.directory, key, output)
