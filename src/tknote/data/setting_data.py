"""
SettingData Class
"""
from __future__ import annotations

from typing import Any, Callable, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    import tkinter as tk


class SettingData:
    def __init__(
        self,
        name: str,
        var: tk.Variable,
        callback: Callable,
        callback_arg_name: str,
        input_type: str,
        options: Iterable | None = None
    ):
        self.name: str = name
        self.var: tk.Variable = var
        self.callback = callback
        self.callback_arg_name: str = callback_arg_name
        self.input_type: str = input_type
        self.options: Iterable | None = options

    @property
    def value(self) -> Any:
        return self.var.get()

    @value.setter
    def value(self, value: Any) -> None:
        self.var.set(value)
