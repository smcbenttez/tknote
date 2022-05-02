"""
SettingsItem
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Type, TypeAlias, TYPE_CHECKING, Union

from tknote.widgets.quantized_scale import QuantizedScale

if TYPE_CHECKING:
    from tknote.widgets.settings import Settings


InputWidgetType: TypeAlias = Union[
    Type[ttk.Button],
    Type[ttk.Combobox],
    Type[ttk.Entry],
    Type[ttk.Scale],
    Type[QuantizedScale]
]

class SettingsItem(tk.Frame):
    def __init__(
        self,
        parent: Settings,
        setting_name: str,
        input_widget_type: InputWidgetType,
        var: tk.Variable,
        **kwargs
    ):
        super().__init__(parent, class_='SettingsItem')
        self.parent = parent
        self.setting_name = setting_name
        self.var = var
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.label = tk.Label(
            self,
            text=self.setting_name,
            justify=tk.RIGHT,
        )
        self.label.grid(
            column=0,
            row=0,
            sticky=tk.E
        )
        self.input_widget = input_widget_type(self)
        self.input_widget.grid(
            column=1,
            row=0,
            sticky=tk.E
        )
        if isinstance(self.input_widget, ttk.Combobox):
            self.input_widget.configure(textvariable=var)
        elif isinstance(self.input_widget, ttk.Scale):
            self.input_widget.configure(variable=var)   # type: ignore

        if isinstance(self.input_widget, ttk.Combobox):
            self.input_widget.configure(
                values=kwargs['options']
            )

        self.var.trace_add("write", self.modified)

    def modified(self, *args) -> None:
        self.event_generate('<<SettingModified>>')
