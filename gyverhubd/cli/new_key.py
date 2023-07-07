import getpass
import sys

from Crypto.PublicKey import DSA


def do_new_key(args):
    password = None
    if args.password:
        password = getpass.getpass("Password: ")
        password2 = getpass.getpass("Repeat password: ")

        if password != password2:
            print("Passwords not match!", file=sys.stderr)
            sys.exit(1)

    key = DSA.generate(3072)
    data = key.export_key(pkcs8=True, passphrase=password)
    args.file.write(data)
