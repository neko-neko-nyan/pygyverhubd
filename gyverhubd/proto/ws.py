import sys

from aiohttp import web
from websockets import server
from websockets.exceptions import ConnectionClosed

from gyverhubd.proto.proto import Protocol, MessageHandler, Request

PYTHON_VERSION = "{}.{}".format(*sys.version_info)
SERVER_NAME = f"Python/{PYTHON_VERSION} gyverhubd/0.0.1"
_FOCUSED_PROP = f'__{__name__.replace(".", "")}_focused'


class WSRequest(Request):
    def __init__(self, protocol, ws, data):
        self.protocol: WSProtocol = protocol
        self._ws = ws

        assert isinstance(data, str) and data and data[-1] == '\0'
        url, eq, value = data[:-1].partition('=')
        if not eq:
            value = None

        self.url = url
        self.value = value

    async def respond(self, data: dict):
        await self.protocol.send_to(self._ws, data)

    def set_focused(self, value: bool):
        setattr(self._ws, _FOCUSED_PROP, value)


class WSProtocol(Protocol):
    def __init__(self, host="", http_port=80, ws_port=81):
        self._host = host
        self._http_port = http_port
        self._ws_port = ws_port

        self._clients = {}
        self._handler: MessageHandler = lambda x: None
        self._ws_srv = None
        self._http_srv = None

    @property
    def focused(self) -> bool:
        return any((getattr(i, _FOCUSED_PROP, False) for i in self._clients.values()))

    def set_handler_message(self, handler):
        self._handler = handler

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

    async def _handle_ws(self, ws: server.WebSocketServerProtocol):
        self._clients[ws.remote_address] = ws

        try:
            while not ws.closed:
                try:
                    data = await ws.recv()
                except ConnectionClosed:
                    pass
                else:
                    self._handler(WSRequest(self, ws, data))

        finally:
            del self._clients[ws.remote_address]

    async def send(self, data: dict):
        for i in tuple(self._clients.values()):
            await self.send_to(i, data)

    async def send_to(self, ws, data: dict):
        data['id'] = self.device_id
        data = '\n' + json.dumps(data) + '\n'
        await ws.send(data)
