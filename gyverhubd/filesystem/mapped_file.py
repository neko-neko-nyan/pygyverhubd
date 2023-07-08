import os
import typing

from . import Filesystem, vfspath
from .. import FileNotExistsError, FilePermissionsError, GyverHubError

__all__ = ['MappedFile']


class MappedFile(Filesystem):
    __slots__ = ('_path', '_allow_delete', 'size')

    def __init__(self, path, *, size=0, allow_delete=True):
        super().__init__()
        self.size = size
        self._path = path
        self._allow_delete = allow_delete

    # ======== #
    @property
    def used(self):
        try:
            return os.path.getsize(self._path)
        except FileNotFoundError:
            return 0
        except PermissionError:
            raise FilePermissionsError()
        except OSError as e:
            raise GyverHubError(e.strerror)

    def get_files_info(self) -> typing.Dict[str, int]:
        return {'': self.used}

    def open(self, path: str, mode="rb"):
        path = vfspath.normpath(path)
        if path != '/':
            raise FileNotExistsError()

        try:
            return open(self._path, mode)
        except FileNotFoundError:
            raise FileNotExistsError()
        except PermissionError:
            raise FilePermissionsError()
        except OSError as e:
            raise GyverHubError(e.strerror)

    def delete(self, path: str):
        path = vfspath.normpath(path)
        if path != '/':
            raise FileNotExistsError()
        if not self._allow_delete:
            raise FilePermissionsError()

        try:
            os.remove(self._path)
        except FileNotFoundError:
            raise FileNotExistsError()
        except PermissionError:
            raise FilePermissionsError()
        except OSError as e:
            raise GyverHubError(e.strerror)

    def rename(self, path: str, new_path: str):
        path = vfspath.normpath(path)
        new_path = vfspath.normpath(new_path)
        if path != new_path:
            raise FilePermissionsError()

    def format(self):
        if not self._allow_delete:
            return

        try:
            os.remove(self._path)
        except FileNotFoundError:
            raise FileNotExistsError()
        except PermissionError:
            raise FilePermissionsError()
        except OSError as e:
            raise GyverHubError(e.strerror)
