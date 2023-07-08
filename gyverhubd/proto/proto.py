import typing

from gyverhubd import parse_url

__all__ = ["Protocol", "Request"]


class Protocol:
    focused: bool = False

    def bind(self, server):
        raise NotImplementedError()

    async def send(self, data: dict):
        raise NotImplementedError()


class Request:
    prefix: str
    clid: typing.Optional[str]
    did: typing.Optional[str]
    cmd: typing.Optional[str]
    name: typing.Optional[str]
    value: typing.Optional[str]
    protocol: Protocol

    def __init__(self, url: str, value: str):
        self.prefix, self.clid, self.did, self.cmd, self.name = parse_url(url)
        self.value = value

    async def respond(self, data: dict):
        raise NotImplementedError()

    def set_focused(self, value: bool):
        raise NotImplementedError()
