import io
import typing

from . import vfspath, VirtualFile, Filesystem, MappedFile
from .. import FileNotExistsError

__all__ = ['UnionFilesystem']


class UnionFilesystem(Filesystem):
    __slots__ = ('_maps', )

    def __init__(self):
        super().__init__()
        self._maps: typing.Dict[str, Filesystem] = {}

    def add(self, prefix: str, fs: Filesystem) -> 'UnionFilesystem':
        prefix = vfspath.normpath(prefix)
        self._maps[prefix] = fs
        return self

    def virtual_file(self, path, size=0, used=0) -> typing.Callable[[typing.Callable[[], bytes]], VirtualFile]:
        def _wr(fn: typing.Callable[[], bytes]):
            vf = VirtualFile(fn, size=size, used=used)
            self.add(path, vf)
            return vf
        return _wr

    def map_file(self, path, fs_path, size=0, allow_delete=True):
        self.add(path, MappedFile(fs_path, size=size, allow_delete=allow_delete))
        return self

    # ======== #

    def _get_fs(self, path: str) -> typing.Tuple[Filesystem, str]:
        path = vfspath.split_all(path)
        for i in range(len(path), -1, -1):
            prefix = vfspath.join_all(*path[:i])
            fs = self._maps.get(prefix)
            if fs is not None:
                return fs, vfspath.join_all(*path[i:])

        raise FileNotExistsError()

    @property
    def used(self):
        return sum((fs.used for fs in self._maps.values()))

    @property
    def size(self):
        return sum((fs.size for fs in self._maps.values()))

    def get_files_info(self) -> typing.Dict[str, int]:
        res = {}
        for prefix, fs in self._maps.items():
            for name, size in fs.get_files_info().items():
                res[vfspath.join(prefix, name)] = size

        return res

    def get_contents(self, path: str) -> bytes:
        fs, path = self._get_fs(path)
        return fs.get_contents(path)

    def put_contents(self, path: str, data: bytes):
        fs, path = self._get_fs(path)
        fs.put_contents(path, data)

    def create(self, path: str):
        fs, path = self._get_fs(path)
        fs.create(path)

    def open(self, path: str, mode="rb") -> io.IOBase:
        fs, path = self._get_fs(path)
        return fs.open(path, mode)

    def delete(self, path: str):
        fs, path = self._get_fs(path)
        fs.delete(path)

    def rename(self, path: str, new_path: str):
        fs, path = self._get_fs(path)
        fs2, new_path = self._get_fs(new_path)
        if fs is fs2:
            fs.rename(path, new_path)
        else:
            data = fs.get_contents(path)
            fs2.put_contents(new_path, data)
            fs.delete(path)

    def format(self):
        for fs in self._maps.values():
            fs.format()
