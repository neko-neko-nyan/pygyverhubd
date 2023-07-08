import binascii
import io
import typing

from .. import response, Module, ReadonlyFilesystemError, request

__all__ = ["Filesystem"]


class Filesystem:
    __slots__ = ('__fetch_temp', '__upload_data', '__upload_name', '_device', 'writable')

    size: int
    used: int
    writable: bool

    # Overridable

    def get_files_info(self) -> typing.Dict[str, int]:
        pass

    def get_contents(self, path: str) -> bytes:
        with self.open(path, "rb") as f:
            return f.read()

    def format(self):
        pass

    def delete(self, path: str):
        pass

    def rename(self, path: str, new_path: str):
        pass

    def put_contents(self, path: str, data: bytes):
        with self.open(path, "wb") as f:
            f.write(data)
        pass

    def create(self, path: str):
        self.put_contents(path, b'')

    def open(self, path: str, mode="rb") -> io.IOBase:
        if mode == "rb":
            return io.BytesIO(self.get_contents(path))
        if mode in {"r", "rt"}:
            return io.StringIO(self.get_contents(path).decode())
        raise NotImplementedError()

    # internal

    def __init__(self):
        self.__fetch_temp = None
        self.__upload_data = self.__upload_name = None
        self.writable = True

    @property
    def disabled_modules(self):
        value = 0
        fst = type(self)

        if not self.writable:
            value |= Module.RENAME | Module.FORMAT | Module.DELETE | Module.UPLOAD

        else:
            if fst.format == Filesystem.format:
                value |= Module.FORMAT
            if fst.rename == Filesystem.rename:
                value |= Module.RENAME
            if fst.delete == Filesystem.delete:
                value |= Module.DELETE

        return value

    async def on_message(self) -> typing.Optional[dict]:
        cmd = request.cmd
        if cmd == "fsbr":
            return self._send_fsbr()

        if cmd == "fetch":
            self.__fetch_temp = self.get_contents(request.name)
            return response("fetch_start")

        if cmd == "fetch_chunk":
            if self.__fetch_temp is None:
                return response("fetch_err")

            res = response("fetch_next_chunk", chunk=0, amount=1,
                           data=binascii.b2a_base64(self.__fetch_temp, newline=False).decode('ascii'))
            self.__fetch_temp = None
            return res

        if not self.writable:
            raise ReadonlyFilesystemError()

        if cmd == "format":
            self.format()
            return response("OK")

        if cmd == "rename":
            self.rename(request.name, request.value)
            return self._send_fsbr()

        if cmd == "delete":
            self.delete(request.name)
            return self._send_fsbr()

        if cmd == "upload":
            self.create(request.name)
            self.__upload_name = request.name
            self.__upload_data = []
            return response("upload_start")

        if cmd == "upload_chunk":
            if self.__upload_data is None:
                return response("upload_err")

            self.__upload_data.append(binascii.a2b_base64(request.value.encode('ascii')))

            if request.name == 'next':
                return response("upload_next_chunk")

            else:
                self.put_contents(self.__upload_name, b''.join(self.__upload_data))
                self.__upload_name = self.__upload_data = None
                return response("upload_end")

    def _send_fsbr(self):
        fs = self.get_files_info()
        # Allow to calculate used space in get_files_info()
        return response("fsbr", total=self.size, used=self.used, fs=fs)
