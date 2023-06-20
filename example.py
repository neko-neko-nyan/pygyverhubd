import asyncio

from gyverhubd import Device, Server
from gyverhubd.proto.ws import WSProtocol


async def main():
    dev = Device(name="Test", did=12345)
    server = Server(dev)
    server.add_protocol(WSProtocol())
    await server.start()
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await server.stop()


if __name__ == '__main__':
    asyncio.run(main())
