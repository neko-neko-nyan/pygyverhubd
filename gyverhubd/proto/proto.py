

class Protocol:
    def bind(self, server):
        raise NotImplementedError()

    async def start(self):
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()
