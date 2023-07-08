import asyncio
import json
import sys

from aiohttp import web
from websockets import server as ws_server
from websockets.exceptions import ConnectionClosed

from . import Protocol, Request
from .. import __version__

__all__ = ["WSProtocol", "protocol_factory"]
HUB_SP = ws_server.Subprotocol("hub")
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
        server.add_event_listener('start', self.__server_start)
        server.add_event_listener('stop', self.__server_stop)

    async def __server_start(self):
        self._ws_srv = await ws_server.serve(self._handle_ws, self._host, self._ws_port, subprotocols=[HUB_SP],
                                             server_header=SERVER_NAME)

        app = web.Application()
        app.on_response_prepare.append(self._on_http_end)
        app.router.add_route('GET', '/hub_discover_all', self._discover_handler)
        app.router.add_route('GET', '/hub_http_cfg', self._config_handler)
        app.router.add_route('POST', '/upload', self._upload_handler)
        app.router.add_route('POST', '/ota', self._ota_handler)
        app.router.add_route('GET', '/fs/{path}', self._fs_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        self._http_srv = web.TCPSite(runner, self._host, self._http_port)
        await self._http_srv.start()

    async def __server_stop(self):
        await self._http_srv.stop()

        self._ws_srv.close()
        await self._ws_srv.wait_closed()

    @staticmethod
    async def _on_http_end(_, res):
        res.headers['Server'] = SERVER_NAME
        res.headers['Access-Control-Allow-Origin'] = '*'

    @staticmethod
    async def _discover_handler(_):
        return web.Response(text="OK")

    @staticmethod
    async def _config_handler(_):
        config = dict(upload=1, download=0, ota=1, path="/fs")
        return web.Response(text=json.dumps(config))

    async def _upload_handler(self, req: web.Request):
        post = await req.post()
        file = post.get('upload')
        if file is None:
            return web.Response(status=400, reason="Missing upload field")
        if not isinstance(file, web.FileField):
            return web.Response(status=400, reason="Upload field must be file")

        name = file.filename
        data = file.file.read()
        await self._server.dispatch_event("request.upload", name, data)

        return web.Response()

    async def _ota_handler(self, req: web.Request):
        post = await req.post()
        part = req.query.get('type')
        if part is None:
            return web.Response(status=400, text='FAIL', reason="Missing part field")

        file = post.get(part)
        if file is None:
            return web.Response(status=400, text='FAIL', reason="Missing upload field")
        if not isinstance(file, web.FileField):
            return web.Response(status=400, text='FAIL', reason="Upload field must be file")

        data = file.file.read()
        await self._server.dispatch_event("request.ota", part, data)

        return web.Response(text='OK')

    @staticmethod
    async def _fs_handler(_: web.Request):
        return web.Response(text='FAIL', status=404)

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
                    asyncio.ensure_future(self._server.dispatch_event('request', req))

        finally:
            del self._clients[ws.remote_address]

    async def send(self, data: dict):
        data = '\n' + json.dumps(data) + '\n'
        for i in tuple(self._clients.values()):
            await i.send(data)


protocol_factory = WSProtocol
