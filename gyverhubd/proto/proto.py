__all__ = ["Protocol", "Request"]

from gyverhubd import parse_url


class Protocol:
    focused: bool = False

    def bind(self, server):
        raise NotImplementedError()

    async def send(self, data: dict):
        raise NotImplementedError()


class Request:
    prefix: str
    clid: str | None
    did: str | None
    cmd: str | None
    name: str | None
    value: str | None
    protocol: Protocol

    def __init__(self, url: str, value: str):
        self.prefix, self.clid, self.did, self.cmd, self.name = parse_url(url)
        self.value = value

    async def respond(self, data: dict):
        raise NotImplementedError()

    def set_focused(self, value: bool):
        raise NotImplementedError()
