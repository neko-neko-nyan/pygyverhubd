import os
import typing

__all__ = ['split_all', 'join_all', 'normpath', 'join', 'sys2vfs']


def split_all(path: str) -> typing.List[str]:
    comps = path.split('/')
    new_comps = []
    for comp in comps:
        if comp in ('', '.'):
            continue

        if comp != '..' or not new_comps or new_comps and new_comps[-1] == '..':
            new_comps.append(comp)
        else:
            if new_comps:
                new_comps.pop()

    return new_comps


def join_all(*parts: str) -> str:
    return '/' + '/'.join(parts)


def sys2vfs(*paths: str) -> str:
    paths = os.path.normpath(os.path.join(*paths)).split(os.path.sep)
    return join_all(*paths)


def normpath(path: str) -> str:
    return join_all(*split_all(path))


def join(a: str, b: str) -> str:
    if a == '/':
        return b
    return a + b
