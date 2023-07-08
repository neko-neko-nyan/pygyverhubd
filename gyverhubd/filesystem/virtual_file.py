import typing

from . import Filesystem, vfspath
from .. import FileNotExistsError, FilePermissionsError, device

__all__ = ['VirtualFile']


class VirtualFile(Filesystem):
    __slots__ = ('fget', 'fset', 'fdel', 'size', 'used')

    def __init__(self, fget=None, fset=None, fdel=None, *, size=0, used=0):
        super().__init__()
        self.size = size
        self.used = used
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def getter(self, fn):
        self.fget = fn
        return self

    def setter(self, fn):
        self.fset = fn
        return self

    def deleter(self, fn):
        self.fdel = fn
        return self

    # ======== #

    def get_files_info(self) -> typing.Dict[str, int]:
        return {'': self.used}

    def get_contents(self, path: str) -> bytes:
        path = vfspath.normpath(path)
        if path != '/':
            raise FileNotExistsError()
        if self.fget is None:
            raise FilePermissionsError()
        return self.fget(device)

    def create(self, path: str):
        path = vfspath.normpath(path)
        if path != '/':
            raise FileNotExistsError()

    def put_contents(self, path: str, data: bytes):
        path = vfspath.normpath(path)
        if path != '/':
            raise FileNotExistsError()
        if self.fset is None:
            raise FilePermissionsError()
        self.fset(device, data)

    def delete(self, path: str):
        path = vfspath.normpath(path)
        if path != '/':
            raise FileNotExistsError()
        if self.fdel is None:
            raise FilePermissionsError()
        self.fdel(device)

    def rename(self, path: str, new_path: str):
        path = vfspath.normpath(path)
        new_path = vfspath.normpath(new_path)
        if path != new_path:
            raise FilePermissionsError()

    def format(self):
        if self.fdel is not None:
            self.fdel(device)
