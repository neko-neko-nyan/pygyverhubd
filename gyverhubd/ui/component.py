import enum
import typing

__all__ = ["Component", "ChangeType"]


class ChangeType(enum.Enum):
    NO = enum.auto()
    UPDATE = enum.auto()
    FULL = enum.auto()


class Component:
    __slots__ = ('__changed__', '__data__', '__handlers__', '__layout__', '__enabled__')
    __type__: str
    __fields__: typing.Tuple[typing.Tuple[str, str, typing.Any], ...] = ()
    __value_field__: typing.Optional[typing.Tuple[str, str, typing.Any]] = None

    __changed__: ChangeType
    __data__: dict
    __handlers__: typing.List[callable]
    __layout__: 'Layout'
    __enabled__: bool

    def __init_subclass__(cls, **kwargs):
        fields = ()
        for i in cls.mro():
            fields += getattr(i, '__fields__', ())
        cls.__fields__ = fields
        return super().__init_subclass__(**kwargs)

    def __set_name__(self, owner, name):
        self.__layout__ = owner
        if self.name is None:
            self.name = name

    def __init__(self, label=None, **kwargs):
        self.__data__ = {name: kwargs.get(name, default) for name, json, default in type(self).__fields__}
        if type(self).__value_field__ is not None:
            name, json, default = type(self).__value_field__
            self.__data__[name] = kwargs.get(name, default)
        self.__handlers__ = []
        self.__changed__ = ChangeType.FULL
        if 'disabled' in kwargs:
            self.__enabled__ = not kwargs.pop('disabled')
        else:
            self.__enabled__ = True

        self.name = None
        self.label = label

    def to_json(self):
        res = {json: getattr(self, name) for name, json, default in type(self).__fields__}
        res['label'] = '_no' if self.label is None else self.label
        res['name'] = self.name
        if hasattr(self, 'tab_w'):
            res['tab_w'] = self.tab_w

        res['type'] = type(self).__type__
        if type(self).__value_field__ is not None:
            name, json, default = type(self).__value_field__
            if json is not None:
                res[json] = self.value2event(getattr(self, name))
        self.__changed__ = ChangeType.NO
        return res

    def rebuild_required(self):
        return self.__changed__ == ChangeType.FULL

    def to_update(self):
        if type(self).__value_field__ is None or self.__changed__ != ChangeType.UPDATE:
            return None
        self.__changed__ = ChangeType.NO
        return self.value2event(getattr(self, type(self).__value_field__[0]))

    def __setattr__(self, key, value):
        if key == '__enabled__' and value != getattr(self, key, None):
            self.__changed__ = ChangeType.FULL
        if key in {'__changed__', '__data__', '__handlers__', '__layout__', '__enabled__'}:
            return super().__setattr__(key, value)
        if self.__changed__ != ChangeType.FULL and value != getattr(self, key, None) and self.__enabled__:
            if type(self).__value_field__ is not None and key == type(self).__value_field__[0]:
                self.__changed__ = ChangeType.UPDATE
            else:
                self.__changed__ = ChangeType.FULL
        self.__data__[key] = value

    def __getattr__(self, item):
        try:
            return self.__data__[item]
        except KeyError as e:
            raise AttributeError from e

    def event2value(self, value: str):
        return value

    def value2event(self, value):
        return value

    async def on_event(self, value):
        value = self.event2value(value)
        if type(self).__value_field__ is not None:
            setattr(self, type(self).__value_field__[0], value)
        self._invoke_handlers(value)

    def _invoke_handlers(self, value):
        for i in self.__handlers__:
            i(self.__layout__, value)

    def add_handler(self, fn):
        self.__handlers__.append(fn)

    def changed(self, fn):
        self.add_handler(fn)
        return fn
