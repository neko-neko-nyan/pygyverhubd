import os
import typing

from . import vfspath, Filesystem
from .. import rmtree_exc, FileNotExistsError, FilePermissionsError, GyverHubError

__all__ = ['MappedFilesystem']


class MappedFilesystem(Filesystem):
    __slots__ = ('_base', 'size', 'used')

    def __init__(self, basedir: str, *, size=0, rw=True):
        super().__init__()
        self.writable = rw
        self.size = size
        self.used = 0
        self._base = os.path.realpath(basedir)
        os.makedirs(self._base, exist_ok=True)

    def _map(self, path: str) -> str:
        path = os.path.join(self._base, *vfspath.split_all(path))
        if os.path.commonpath((path, self._base)) != self._base:
            raise FileNotExistsError()

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except FileNotFoundError:
            raise FileNotExistsError()
        except PermissionError:
            raise FilePermissionsError()
        except OSError as e:
            raise GyverHubError(e.strerror)

        return path

    def get_files_info(self) -> typing.Dict[str, int]:
        self.used = 0
        res = {}
        for root, dirs, files in os.walk(self._base, topdown=True, followlinks=False):
            vfs_root = os.path.relpath(root, self._base)

            for filename in files:
                try:
                    size = os.path.getsize(os.path.join(root, filename))
                except OSError:
                    size = 0

                res[vfspath.sys2vfs(vfs_root, filename)] = size
                self.used += size
        return res

    def open(self, path: str, mode="rb"):
        path = self._map(path)
        try:
            return open(path, mode)
        except FileNotFoundError:
            raise FileNotExistsError()
        except PermissionError:
            raise FilePermissionsError()
        except OSError as e:
            raise GyverHubError(e.strerror)

    def delete(self, path: str):
        path = self._map(path)
        try:
            os.remove(path)
        except FileNotFoundError:
            raise FileNotExistsError()
        except PermissionError:
            raise FilePermissionsError()
        except OSError as e:
            raise GyverHubError(e.strerror)

    def rename(self, path: str, new_path: str):
        path = self._map(path)
        new_path = self._map(new_path)
        if path != new_path:
            try:
                os.rename(path, new_path)
            except FileNotFoundError:
                raise FileNotExistsError()
            except PermissionError:
                raise FilePermissionsError()
            except OSError as e:
                raise GyverHubError(e.strerror)

    def format(self):
        self.used = 0
        try:
            rmtree_exc(self._base)
        except FileNotFoundError:
            raise FileNotExistsError()
        except PermissionError:
            raise FilePermissionsError()
        except OSError as e:
            raise GyverHubError(e.strerror)
        os.makedirs(self._base, exist_ok=True)
