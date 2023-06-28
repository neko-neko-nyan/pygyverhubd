import asyncio
import json
import sys

from aiohttp import web
from websockets import server as ws_server
from websockets.exceptions import ConnectionClosed

from . import Protocol, Request
from .. import __version__


SERVER_NAME = f"Python/{sys.version.partition(' ')[0]} gyverhubd/{__version__}"
_FOCUSED_PROP = f'__focused'


class WSRequest(Request):
    def __init__(self, protocol, ws, data):
        self.protocol: WSProtocol = protocol
        self._ws = ws

        assert isinstance(data, str) and data and data[-1] == '\0'
        url, eq, data = data[:-1].partition('=')
        super().__init__(url, data if eq else None)

    async def respond(self, data: dict):
        if self.did is not None:
            data['id'] = self.did
        data = '\n' + json.dumps(data) + '\n'
        await self._ws.send(data)

    def set_focused(self, value: bool):
        setattr(self._ws, _FOCUSED_PROP, value)


class WSProtocol(Protocol):
    def __init__(self, host="", http_port=80, ws_port=81):
        self._host = host
        self._http_port = http_port
        self._ws_port = ws_port

        self._clients = {}
        self._server = None
        self._ws_srv = None
        self._http_srv = None

    @property
    def focused(self) -> bool:
        return any((getattr(i, _FOCUSED_PROP, False) for i in self._clients.values()))

    def bind(self, server):
        self._server = server

    async def start(self):
        self._ws_srv = await ws_server.serve(self._handle_ws, self._host, self._ws_port, subprotocols=["hub"],
                                             server_header=SERVER_NAME)

        app = web.Application()
        app.on_response_prepare.append(self._on_http_end)
        app.router.add_route('GET', '/hub_discover_all', self._discover_handler)
        app.router.add_route('GET', '/hub_http_cfg', self._config_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        self._http_srv = web.TCPSite(runner, self._host, self._http_port)
        await self._http_srv.start()

    async def stop(self):
        await self._http_srv.stop()

        self._ws_srv.close()
        await self._ws_srv.wait_closed()

    async def _on_http_end(self, _, res):
        res.headers['Server'] = SERVER_NAME

    async def _discover_handler(self, _):
        return web.Response(text="OK", headers={'Access-Control-Allow-Origin': '*'})

    async def _config_handler(self, _):
        config = dict(upload=0, download=0, ota=0, path="/")
        return web.Response(text=json.dumps(config), headers={'Access-Control-Allow-Origin': '*'})

    async def _handle_ws(self, ws: ws_server.WebSocketServerProtocol):
        self._clients[ws.remote_address] = ws

        try:
            while not ws.closed:
                try:
                    data = await ws.recv()
                except ConnectionClosed:
                    pass
                else:
                    req = WSRequest(self, ws, data)
                    asyncio.ensure_future(self._server.handle_request(req))

        finally:
            del self._clients[ws.remote_address]

    async def send(self, data: dict):
        data = '\n' + json.dumps(data) + '\n'
        for i in tuple(self._clients.values()):
            await i.send(data)


protocol_factory = WSProtocol
