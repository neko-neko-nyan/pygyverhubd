import asyncio
import json
import sys

from aiohttp import web
from websockets.exceptions import ConnectionClosed

from gyverhubd.proto.proto import Protocol
from websockets import server


PYTHON_VERSION = "{}.{}".format(*sys.version_info)
SERVER_NAME = f"Python/{PYTHON_VERSION} gyverhubd/0.0.1"


class WSProtocol(Protocol):
    def __init__(self, host="", http_port=80, ws_port=81):
        self._server = None
        self._ws_srv = None
        self._http_srv = None
        self._host = host
        self._http_port = http_port
        self._ws_port = ws_port

    def bind(self, server):
        self._server = server

    async def start(self):
        self._ws_srv = await server.serve(self._handle_ws, self._host, self._ws_port, subprotocols=["hub"],
                                          server_header=SERVER_NAME)

        app = web.Application()
        app.router.add_route('GET', '/hub_discover_all', self._discover_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        self._http_srv = web.TCPSite(runner, self._host, self._http_port)
        await self._http_srv.start()

    async def stop(self):
        await self._http_srv.stop()

        self._ws_srv.close()
        await self._ws_srv.wait_closed()

    async def _discover_handler(self, _):
        return web.Response(text="OK", headers={'Access-Control-Allow-Origin': '*'})

    async def _receiver(self, ws, client):
        while not ws.closed:
            try:
                data = await ws.recv()
            except ConnectionClosed:
                pass
            else:
                assert isinstance(data, str) and data and data[-1] == '\0'
                url, eq, value = data[:-1].partition('=')
                if not eq:
                    value = None

                await client.got_data(url, value)

    async def _handle_ws(self, ws: server.WebSocketServerProtocol):
        client = self._server.connected(ws.remote_address)
        asyncio.ensure_future(self._receiver(ws, client))

        while not ws.closed:
            msg = await client.get_message()
            try:
                await ws.send('\n' + json.dumps(msg) + '\n')
            except ConnectionClosed:
                pass

        client.disconnected(ws.close_code)
