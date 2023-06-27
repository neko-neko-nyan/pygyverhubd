__all__ = ["DeviceUi"]


class DeviceUi:
    async def on_update(self) -> dict:
        raise NotImplementedError()

    async def on_ui_event(self, name: str, value: str) -> dict:
        raise NotImplementedError()
