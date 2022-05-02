"""
WidgetDelegate Abstract Class
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tkinter import font as tk_font


class WidgetDelegate(ABC):  # pylint: disable=too-few-public-methods
    """
    An abstract class extending :py:class:`abc.ABC`
    that defines the delegate methods for the custom
    widgets in :py:mod:`tknote`
    """

    @property
    @abstractmethod
    def font(self) -> tk_font.Font:
        """
        Get the application font

        :abstractmethod:
        :type: :py:class:`tkinter.font.Font`
        """
        ...
