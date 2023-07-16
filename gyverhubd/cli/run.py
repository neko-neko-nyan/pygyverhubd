import importlib
import os
import sys
import zipfile

from gyverhubd import run_server
from gyverhubd.proto.mqtt import MqttProtocol
from gyverhubd.proto.serial import SerialProtocol
from gyverhubd.proto.websocket import WebsocketProtocol


def import_device(main: str):
    module, _, cls = main.rpartition('.')
    loaded = module in sys.modules
    mod = __import__(module)
    if loaded:
        importlib.reload(mod)

    for i in module.split('.')[1:]:
        mod = getattr(mod, i)

    return getattr(mod, cls)


def get_main_device(path):
    if path.is_dir():
        main = path / 'MAIN'
        if not main.exists():
            print("No device to run specified and no MAIN file found!", file=sys.stderr)
            sys.exit(1)

        return main.read_text('utf-8')

    else:
        with zipfile.ZipFile(path) as zf:
            try:
                main = zf.getinfo('MAIN')
            except KeyError:
                print("No device to run specified and package has no MAIN device!", file=sys.stderr)
                sys.exit(1)

            return zf.read(main).decode('utf-8')


def do_run2(args):
    protocols = []
    devices = []

    if args.websocket is not None:
        options = (i.partition('=') for i in args.mqtt_option)
        protocols.append(WebsocketProtocol(args.websocket, {k: v for k, _, v in options}))

    if args.mqtt is not None:
        options = (i.partition('=') for i in args.mqtt_option)
        protocols.append(MqttProtocol(args.mqtt, {k: v for k, _, v in options}))

    if args.serial is not None:
        options = (i.partition('=') for i in args.serial_option)
        protocols.append(SerialProtocol(args.serial, {k: v for k, _, v in options}))

    path = str(args.path.resolve())
    if path not in sys.path:
        sys.path.append(path)

    cached = sys.path_importer_cache.get(path)
    if cached is not None:
        cached.invalidate_caches()
        del sys.path_importer_cache[path]

    if args.device is None:
        args.device = [get_main_device(args.path)]

    for i in args.device:
        dev_cls = import_device(i)
        devices.append(dev_cls())

    run_server(*devices, protocols=protocols)


def do_run(args):
    while True:
        os.environ['__SRV_AUTO_RESTART'] = ''
        os.environ['__SRV_OTA'] = ''

        do_run2(args)

        if os.environ.get('__SRV_OTA'):
            path = args.path
            tmp = path.with_suffix(args.path.suffix + '.tmp')
            bak = path.with_suffix(args.path.suffix + '.bak')

            path.rename(bak)
            try:
                tmp.rename(path)
            except OSError:
                bak.rename(path)
            else:
                bak.unlink()

        if not os.environ.get('__SRV_AUTO_RESTART'):
            break
