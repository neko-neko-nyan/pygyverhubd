import typing


MessageHandler = typing.Callable[['Request'], None]


class Protocol:
    def set_handler_message(self, handler: MessageHandler):
        raise NotImplementedError()

    async def send(self, data: str):
        raise NotImplementedError()

    async def start(self):
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()


class Request:
    url: str
    value: str | None
    protocol: Protocol

    async def respond(self, data: str):
        raise NotImplementedError()
