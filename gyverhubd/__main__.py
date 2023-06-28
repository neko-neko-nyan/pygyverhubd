import asyncio
import sys

from gyverhubd import Server
from gyverhubd.config import Config


HELP_TEXT = f"""\
Usage: python3 -m gyverhubd CONFIG_FILE...
windows: py -3 -m gyverhubd CONFIG_FILE...

Start server for devices described in config files.
See wiki for more info.

"""


def make_server_from_config(*files):
    cp = Config()
    for i in files:
        cp.read_file(i)
    cp.finalize()
    return Server(*cp.devices, **cp.server_opts)


async def run_server(server):
    await server.start()
    try:
        await asyncio.Future()
    finally:
        await server.stop()


def main():
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) == 1:
        print(HELP_TEXT)
        return

    server = make_server_from_config(*sys.argv[1:])
    asyncio.run(run_server(server))


main()
