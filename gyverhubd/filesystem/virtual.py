import typing

from . import vfspath, Filesystem
from .. import FileNotExistsError

__all__ = ['VirtualFilesystem']


class VirtualFilesystem(Filesystem):
    __slots__ = ('size', '_data')

    def __init__(self, *, size=0):
        super().__init__()
        self.size = size
        self._data = {}

    @property
    def used(self):
        return sum((len(data) for data in self._data.values()))

    def get_files_info(self) -> typing.Dict[str, int]:
        return {name: len(data) for name, data in self._data.items()}

    def get_contents(self, path: str) -> bytes:
        path = vfspath.normpath(path)
        if path not in self._data:
            raise FileNotExistsError()
        return self._data[path]

    def put_contents(self, path: str, data: bytes):
        path = vfspath.normpath(path)
        self._data[path] = data

    def delete(self, path: str):
        path = vfspath.normpath(path)
        if path not in self._data:
            raise FileNotExistsError()
        del self._data[path]

    def rename(self, path: str, new_path: str):
        path = vfspath.normpath(path)
        new_path = vfspath.normpath(new_path)
        if path not in self._data:
            raise FileNotExistsError()
        if path != new_path:
            self._data[new_path] = self._data[path]
            del self._data[path]

    def format(self):
        self._data = {}
