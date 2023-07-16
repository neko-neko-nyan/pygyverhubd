import argparse
import pathlib


def main():
    parser = argparse.ArgumentParser("gyverhubd", description="The pygyverhubd utilities")

    subparsers = parser.add_subparsers(dest="command", metavar='COMMAND')

    # ====

    run = subparsers.add_parser("run", help="Run device")

    run.add_argument("path", type=pathlib.Path, default=pathlib.Path('.'),
                     help="Path to device package or directory containing device files (default: current directory).")
    run.add_argument("-d", "--device", action='append', metavar='MOD.CLASS',
                     help="Run specified device CLASS from MOD. MOD can be top-level module or package. This option can"
                          " be repeated to run multiple devices in one server (MQTT only).")

    run.add_argument("-w", "--websocket", metavar='HOST[:PORT]', const='', nargs='?',
                     help="Enable WebSocket / HTTP server on specified HOST and PORT (default port is 80 for http and"
                          " 443 for https, default host is all hosts).")
    run.add_argument("--websocket-option", metavar="NAME=VALUE", default=[], action='append',
                     help='Set WebSocket protocol option (try --websocket-option=help=yes to get help)')

    run.add_argument("-m", "--mqtt", metavar="SERVER[:PORT]",
                     help="Enable MQTT connection on specified SERVER and PORT (default port is 1883).")
    run.add_argument("--mqtt-option", metavar="NAME=VALUE", default=[], action='append',
                     help="Set MQTT protocol option (try --mqtt-option=help=yes to get help)")

    run.add_argument("-s", "--serial", metavar="PORT",
                     help="Enable serial connection on specified PORT (on linux PORT must be /dev/ttyX, on Windows it"
                          " may be COMX \\\\.\\CNCX).")
    run.add_argument("--serial-option", metavar="NAME=VALUE", default=[], action='append',
                     help="Set serial connection option (try --serial-option=help=yes to get help)")

    # ====

    new_key = subparsers.add_parser("new-key", help="Generate private key for signing updates.")
    new_key.add_argument("file", type=argparse.FileType('wb'),
                         help="Output private key file (in .pem format)")
    new_key.add_argument("-p", "--password", action='store_true',
                         help="Enable key password protection.")

    pack = subparsers.add_parser("pack", help="Make update / device package")
    pack.add_argument("directory", type=pathlib.Path, default='.', nargs='?',
                      help="Input directory (default: current directory)")
    pack.add_argument("-m", "--main", metavar='MOD.CLASS',
                      help="Make specified device CLASS from MOD default (main). MOD can be top-level module or"
                           " package.")
    pack.add_argument("-s", "--sign", type=argparse.FileType('rt'), metavar='KEY',
                      help="Sign package with specified private KEY.")
    pack.add_argument("-o", "--output", type=argparse.FileType('wb'),
                      help="Output package file (default: directory name with .zip extension)")

    args = parser.parse_args()

    if args.command == 'run':
        from .run import do_run
        do_run(args)

    elif args.command == 'new-key':
        from .new_key import do_new_key
        do_new_key(args)

    elif args.command == 'pack':
        from .pack import do_pack
        do_pack(args)
