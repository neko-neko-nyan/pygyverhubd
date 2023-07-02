import configparser
import os.path
import sys
import types


class _Sections:
    def __init__(self):
        self._items = []

    def __contains__(self, item):
        return False

    def __setitem__(self, key, value):
        self._items.append((key, value))

    def items(self):
        return self._items


class Config(configparser.RawConfigParser):
    def __init__(self):
        super().__init__(delimiters=('=', ), comment_prefixes=None, inline_comment_prefixes=("#", ),
                         empty_lines_in_values=False, strict=False)
        self.protocols = []
        self.devices = []
        self.server_opts = {}
        self._sections = _Sections()

    def read_file(self, path) -> None:
        with open(path, "rt") as f:
            super().read_file(f, path)

    def finalize(self):
        for k, v in self._sections.items():
            if k == 'protocol':
                self.load_protocol(v.pop('name'), v)
            if k == 'device':
                self.load_device(v)
            if k == 'server':
                self.server_opts.update(v)

        self.server_opts['protocols'] = self.protocols

    def load_protocol(self, name, options):
        mod = __import__(f"gyverhubd.proto.{name}", fromlist=('protocol_factory',))
        proto = mod.protocol_factory(**options)
        self.protocols.append(proto)

    def load_device(self, options: dict):
        if 'file' in options:
            file = options['file']
            with open(file, 'rt', encoding='utf-8') as f:
                code = f.read()
            code = compile(code, file, "exec", dont_inherit=True)
            mod = types.ModuleType(os.path.splitext(os.path.basename(file))[0])
            mod.__file__ = file
            exec(code, mod.__dict__)

        else:
            if 'path' in options:
                sys.path.append(options['path'])
            mod = __import__(options['module'])

        device = getattr(mod, options.get('name', 'Device'))()
        self.devices.append(device)
