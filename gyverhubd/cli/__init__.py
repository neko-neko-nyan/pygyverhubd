import argparse
import pathlib


def main():
    parser = argparse.ArgumentParser("gyverhubd", description="The pygyverhubd utilities")

    subparsers = parser.add_subparsers(dest="command", metavar='COMMAND')

    # ====

    run = subparsers.add_parser("run", help="Run device")

    run.add_argument("path", type=pathlib.Path, default=pathlib.Path('.'), help="Path to device package or directory containing device files (default: current directory).")
    run.add_argument("-d", "--device", action='append', metavar='MOD.CLASS', help="Run specified device CLASS from MOD. MOD can be top-level module or package. This option can be repeated to run multiple devices in one server (MQTT only).")

    run.add_argument("-w", "--websocket", action='store_true', help="Enable WebSocket / HTTP server")
    run.add_argument("--websocket-host", default='', metavar='HOST', help="Run server on specific host or IP address (default: all addresses).")
    run.add_argument("--http-port", type=int, default=80, metavar='PORT', help='Run HTTP server on specified PORT (default: 80).')
    run.add_argument("--websocket-port", type=int, default=81, metavar='PORT', help='Run WebSocket server on specified PORT (default: 81).')

    run.add_argument("-m", "--mqtt", metavar="SERVER", help="Enable MQTT connection on specified SERVER.")
    run.add_argument("--mqtt-port", type=int, default=1883, metavar="PORT", help="MQTT port (default: 1883)")
    run.add_argument("--mqtt-username", metavar="USER", help="MQTT server user name (default: do not authenticate)")
    run.add_argument("--mqtt-password", metavar='PASS', help="MQTT server password (default: do not authenticate)")

    # ====

    new_key = subparsers.add_parser("new-key", help="Generate private key for signing updates.")
    new_key.add_argument("file", type=argparse.FileType('wb'), help="Output private key file (in .pem format)")
    new_key.add_argument("-p", "--password", action='store_true', help="Enable key password protection.")

    pack = subparsers.add_parser("pack", help="Make update / device package")
    pack.add_argument("directory", type=pathlib.Path, default='.', nargs='?', help="Input directory (default: current directory)")
    pack.add_argument("-s", "--sign", type=argparse.FileType('rt'), metavar='KEY', help="Sign package with specified private KEY.")
    pack.add_argument("-o", "--output", type=argparse.FileType('wb'), help="Output package file (default: directory name with .zip extension)")

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
