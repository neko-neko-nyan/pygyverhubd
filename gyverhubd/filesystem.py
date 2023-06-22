from . import response


class Filesystem:
    size: int
    used: int
    update_format: str = "bin"

    # Overridable

    def get_files_info(self) -> dict[str, int]:
        pass

    def format(self):
        pass

    def delete(self, path: str):
        pass

    def rename(self, path: str, new_path: str):
        pass

    def get_contents(self, path: str) -> bytes:
        pass

    def put_contents(self, path: str, data: bytes):
        pass

    # internal

    def __init__(self):
        self._fetch_temp = None
        self._upload_data = self._upload_name = None

    async def on_message(self, req, cmd: str, name: str | None) -> dict | None:
        if cmd == "fsbr":
            # not mounted = fs_error
            return self._send_fsbr()

        if cmd == "format":
            try:
                self.format()
            except Exception:
                return response("ERR")
            else:
                return response("OK")

        if cmd == "rename":
            try:
                self.rename(name, req.value)
            except Exception:
                return response("ERR")
            else:
                return self._send_fsbr()

        if cmd == "delete":
            try:
                self.delete(name)
            except Exception:
                return response("ERR")
            else:
                return self._send_fsbr()

        if cmd == "fetch":
            try:
                self._fetch_temp = self.get_contents(name)
            except Exception:
                return response("fetch_err")
            else:
                return response("fetch_start")

        if cmd == "fetch_chunk":
            if self._fetch_temp is None:
                return response("fetch_err")

            self._fetch_temp = None
            return response("fetch_next_chunk", chunk=0, amount=1, data=self._fetch_temp)

        if cmd == "upload":
            try:
                self.put_contents(name, b'')
            except Exception:
                return response("upload_err")
            else:
                self._upload_name = name
                self._upload_data = []
                return response("upload_start")

        if cmd == "upload_chunk":
            if self._upload_data is None:
                return response("upload_err")

            self._upload_data.append(req.value)

            if name == 'next':
                return response("upload_next_chunk")

            elif name == 'last':
                try:
                    self.put_contents(self._upload_name, b''.join(self._upload_data))
                except Exception:
                    return response("upload_err")
                else:
                    self._upload_name = self._upload_data = None
                    return response("upload_end")

    def _send_fsbr(self):
        return response("fsbr", total=self.size, used=self.used, gzip=self.update_format == "gzip",
                        fs=self.get_files_info())
