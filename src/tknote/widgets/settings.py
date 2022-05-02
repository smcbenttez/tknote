"""
SettingsView displays app settings and allows
users to change app settings.
"""
from __future__ import annotations

from abc import abstractmethod
import tkinter as tk
from tkinter import ttk
from typing import List

from tknote.widgets.quantized_scale import QuantizedScale
from tknote.widgets.settings_item import InputWidgetType, SettingsItem
from tknote.widgets.widget_delegate import WidgetDelegate


class Settings(tk.Frame):
    def __init__(
            self,
            parent,
            delegate: SettingsDelegate,
    ):
        super().__init__(parent, class_='Settings')
        self.columnconfigure(0, weight=1)
        self.delegate = delegate

        # subviews
        self.settings_items: List[SettingsItem] = []

    def add_setting(
        self,
        name: str,
        var,
        input_type: str,
        **kwargs
    ) -> None:
        input_widget_type: InputWidgetType
        if input_type == 'button':
            input_widget_type = ttk.Button
        elif input_type == 'combobox':
            input_widget_type = ttk.Combobox
        elif input_type == 'entry':
            input_widget_type = ttk.Entry
        elif input_type == 'scale':
            input_widget_type = ttk.Scale
        elif input_type == 'quantized_scale':
            input_widget_type = QuantizedScale

        new_settings_item = SettingsItem(
            self,
            name,
            input_widget_type,
            var,
            **kwargs
        )
        self.settings_items.append(new_settings_item)
        new_settings_item.bind(
            '<<SettingModified>>',
            self.delegate.setting_modified
        )
        self.rowconfigure(len(self.settings_items) - 1, weight=0)
        new_settings_item.grid(
            column=0,
            row=len(self.settings_items) - 1,
            sticky=(tk.N, tk.S, tk.E, tk.W),     # type: ignore
            padx=(40, 40),
            pady=(20, 20)
        )


class SettingsDelegate(WidgetDelegate):

    @abstractmethod
    def setting_modified(self, event: tk.Event) -> None:
        ...
