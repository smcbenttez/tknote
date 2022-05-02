"""
TkGeometry
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TkGeometry:
    """
    Dataclass to encapsulate and structure tkinter widget geometry data.

    :param args: Iterable representing bounds of widget in the
        order of (width, height, x offset, y offset)
    :type args: :py:class:`typing.Iterable`[int]
    """
    def __init__(self, *args):
        self.width: int = args[0]
        self.height: int = args[1]
        self.x_off: int = args[2]
        self.y_off: int = args[3]

    def __repr__(self) -> str:
        return f"{self.width}x{self.height}+{self.x_off}+{self.y_off}"

    @classmethod
    def from_str(cls, tk_geometry_str: str) -> TkGeometry:
        """
        Create TkGeometry object from a geometry string provided by tkinter.

        :param tk_geometry_str: String provided by a widget's
            `winfo_geometry` function in the format of
            {width}x{height}+{x offset}+{y offset}
        :type tk_geometry_str: str
        :return: An instance of `TkGeometry`
        :rtype: :py:class:`tknote.tk_geometry.TkGeometry`
        """
        return cls(
            *[int(x) for x in tk_geometry_str.replace('x', '+').split('+')]
        )
