"""
SettingsController
"""
from __future__ import annotations

import tkinter as tk
from tkinter import font as tk_font
from typing import Dict, TYPE_CHECKING

from tknote.data.setting_data import SettingData
import tknote.defaults
from tknote.widgets.settings import Settings, SettingsDelegate
from tknote.widgets.settings_item import SettingsItem
from tknote.tk_geometry import TkGeometry
from tknote.utils import int_to_scalar

if TYPE_CHECKING:
    from tknote.app import App
    from tknote.model import Model


class SettingsController(SettingsDelegate):
    """
    SettingsController
    """
    def __init__(self, app_root: App):

        self.app = app_root
        model: Model = self.app.model
        self.settings_window = tk.Toplevel(self.app)
        self.settings_window.title("TkNote Settings")
        self.settings_window.protocol('WM_DELETE_WINDOW', self.on_close)
        self.settings_window.columnconfigure(0, weight=1)
        self.settings_window.rowconfigure(0, weight=1)

        self.settings: Dict[str, SettingData] = {}
        # define settings using SettingData
        # font settings
        font_setting: SettingData = SettingData(
            'Font',
            tk.StringVar(),
            self.app.set_font,
            'font_name',
            'combobox',
            tk_font.families(),
        )
        font_setting.value = self.app.font['family']
        self.settings[font_setting.name] = font_setting
        font_size_setting: SettingData = SettingData(
            'Default Font Size',
            tk.DoubleVar(),
            self.app.set_font,
            'font_size_scalar',
            'quantized_scale',
            tuple(range(1, 65)),
        )
        font_size_setting.value = int_to_scalar(
            val=self.app.font['size'],
            min_val=tknote.defaults.FONT_MIN_SIZE,
            max_val=tknote.defaults.FONT_MAX_SIZE
        )
        self.settings[font_size_setting.name] = font_size_setting
        # list settings
        list_sort_key_setting: SettingData = SettingData(
            'Sort List by',
            tk.StringVar(),
            model.set_data_sort_key,
            'sort_key',
            'combobox',
            ('Time Edited', 'Time Created')
        )
        sort_key = model.data_sort_key
        list_sort_key_setting.value = (
            " ".join([x.capitalize() for x in sort_key.split("_")])
        )
        self.settings[list_sort_key_setting.name] = list_sort_key_setting
        list_sort_ascending_setting: SettingData = SettingData(
            'Sort Order',
            tk.StringVar(),
            model.set_data_sort_order,
            'sort_order',
            'combobox',
            ('Ascending', 'Descending')
        )
        sort_order = 'Descending'
        if model.data_sort_ascending:
            sort_order = 'Ascending'
        list_sort_ascending_setting.value = sort_order
        self.settings[list_sort_ascending_setting.name] = (
            list_sort_ascending_setting
        )

        # create and populate settingsview
        self.settings_view = Settings(self.settings_window, self)
        self.settings_view.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.S, tk.E, tk.W)     # type: ignore
        )
        for _, setting in self.settings.items():
            self.settings_view.add_setting(
                setting.name,
                setting.var,
                setting.input_type,
                options=setting.options
            )

        # TODO: make this better
        main_win_pos = TkGeometry.from_str(self.app.winfo_geometry())
        x = main_win_pos.width//2 + main_win_pos.x_off
        y = main_win_pos.height//2 + main_win_pos.y_off
        self.settings_window.geometry('+%d+%d' % (x, y))

        self.app.event_add('<<SettingModified>>', 'None')

    def on_close(self) -> None:
        # TODO would be interesting to make this more general
        self.app.controller.settings_controller = None
        self.settings_window.destroy()

    # SettingsDelegate methods
    @property
    def font(self) -> tk_font.Font:
        return self.app.font

    def setting_modified(self, event: tk.Event) -> None:
        if isinstance(event.widget, SettingsItem):
            setting = self.settings[event.widget.setting_name]
            kwargs = {setting.callback_arg_name: setting.value}
            setting.callback(**kwargs)
