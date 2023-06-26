import datetime
import time

from gyverhubd import Component


class DateTimeBase(Component):
    __fields__ = (
        ('value', 'value', 0),
        ('color', 'color', None),
    )


class Date(DateTimeBase):
    __value_field__ = ('value', 'value', datetime.date.today())
    __type__ = "date"

    def value2event(self, value: datetime.date):
        return time.mktime(value.timetuple())

    def event2value(self, value):
        value = int(value)
        return datetime.date.fromtimestamp(value)


class Time(DateTimeBase):
    __value_field__ = ('value', 'value', datetime.datetime.now().time())
    __type__ = "time"

    def value2event(self, value: datetime.time):
        return value.hour * 3600 + value.minute * 60 + value.second

    def event2value(self, value):
        value = int(value)
        return datetime.time(value // 3600, (value // 60) % 60, value % 60)


class DateTime(DateTimeBase):
    __value_field__ = ('value', 'value', datetime.datetime.now())
    __type__ = "datetime"

    def value2event(self, value: datetime.datetime):
        return value.timestamp()

    def event2value(self, value):
        value = int(value)
        return datetime.datetime.fromtimestamp(value)

