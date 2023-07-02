__all__ = ["GyverHubError", "ReadonlyFilesystemError", "FileNotExistsError", "FilePermissionsError"]


class GyverHubError(Exception):
    message: str = "Failed"
    type: str = "ERR"

    def __init__(self, message: str = None):
        super().__init__()
        if message is not None:
            self.message = message


class ReadonlyFilesystemError(GyverHubError):
    message = "Read-only filesystem"


class FileNotExistsError(GyverHubError):
    message = "File not exists"


class FilePermissionsError(GyverHubError):
    message = "insufficient permissions"
