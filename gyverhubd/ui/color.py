import colorsys
import typing

__all__ = ["Color"]


class Color(int):
    __slots__ = ()

    @classmethod
    def from_hex(cls, value: int) -> 'Color':
        return cls(value)

    @classmethod
    def from_grayscale(cls, value: int) -> 'Color':
        return cls.from_rgb(value, value, value)

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> 'Color':
        return cls((r << 16) | (g << 8) | (b << 0))

    @classmethod
    def from_rgbf(cls, r: float, g: float, b: float) -> 'Color':
        return cls.from_rgb(int(r * 255), int(g * 255), int(b * 255))

    @classmethod
    def from_hsvf(cls, h: float, s: float, v: float) -> 'Color':
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return cls.from_rgbf(r, g, b)

    @classmethod
    def from_hsv(cls, h: int, s: int, v: int) -> 'Color':
        return cls.from_hsvf(h // 255, s // 255, v // 255)

    @classmethod
    def from_hue(cls, color: int):
        if color > 170:
            shift = (color - 170) * 3
            return cls.from_rgb(shift, 0, 255 - shift)
        elif color > 85:
            shift = (color - 85) * 3
            return cls.from_rgb(0, 255 - shift, shift)
        else:
            shift = color * 3
            return cls.from_rgb(255 - shift, shift, 0)

    RED: typing.ClassVar['Color']
    ORANGE: typing.ClassVar['Color']
    YELLOW: typing.ClassVar['Color']
    GREEN: typing.ClassVar['Color']
    MINT: typing.ClassVar['Color']
    AQUA: typing.ClassVar['Color']
    BLUE: typing.ClassVar['Color']
    VIOLET: typing.ClassVar['Color']
    PINK: typing.ClassVar['Color']
    DEFAULT: typing.ClassVar['Color']


for _k, _v in dict(RED=0xcb2839, ORANGE=0xd55f30, YELLOW=0xd69d27, GREEN=0x37A93C, MINT=0x25b18f, AQUA=0x2ba1cd,
                   BLUE=0x297bcd, VIOLET=0x825ae7, PINK=0xc8589a, DEFAULT=0xffffff).items():
    setattr(Color, _k, Color.from_hex(_v))
del _k
del _v
