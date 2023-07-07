import importlib
import os
import sys

from gyverhubd import run_server
from gyverhubd.proto.mqtt import MqttProtocol
from gyverhubd.proto.ws import WSProtocol


def import_device(main: str):
    module, _, cls = main.rpartition('.')
    loaded = module in sys.modules
    mod = __import__(module)
    if loaded:
        importlib.reload(mod)

    for i in module.split('.')[1:]:
        mod = getattr(mod, i)

    return getattr(mod, cls)


def do_run2(args):
    protocols = []
    devices = []

    if args.websocket:
        protocols.append(WSProtocol(args.websocket_host, args.http_port, args.websocket_port))
    if args.mqtt is not None:
        protocols.append(MqttProtocol(args.mqtt, args.mqtt_port, username=args.mqtt_username,
                                      password=args.mqtt_password))

    path = str(args.path.resolve())
    if path not in sys.path:
        sys.path.append(path)

    cached = sys.path_importer_cache.get(path)
    if cached is not None:
        cached.invalidate_caches()
        del sys.path_importer_cache[path]

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
