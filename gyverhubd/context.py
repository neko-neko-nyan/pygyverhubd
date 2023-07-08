import contextlib
import contextvars

from . import Request, LocalProxy

__all__ = ['request', 'device', 'server', 'request_context', 'device_context', 'server_context']

_cv_request: contextvars.ContextVar[Request] = contextvars.ContextVar("pygyverhubd.request_ctx")
_cv_device: contextvars.ContextVar['Device'] = contextvars.ContextVar("pygyverhubd.device_ctx")
_cv_server: contextvars.ContextVar['Server'] = contextvars.ContextVar("pygyverhubd.server_ctx")
# noinspection PyTypeChecker
request: Request = LocalProxy(_cv_request)
# noinspection PyTypeChecker
device: 'Device' = LocalProxy(_cv_device)
# noinspection PyTypeChecker
server: 'Server' = LocalProxy(_cv_server)


@contextlib.contextmanager
def request_context(req: Request):
    token = _cv_request.set(req)
    try:
        yield None
    finally:
        _cv_request.reset(token)


@contextlib.contextmanager
def device_context(dev):
    token = _cv_device.set(dev)
    try:
        yield None
    finally:
        _cv_device.reset(token)


@contextlib.contextmanager
def server_context(srv):
    token = _cv_server.set(srv)
    try:
        yield None
    finally:
        _cv_server.reset(token)
