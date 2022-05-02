"""
App Class
"""
import tkinter as tk
from tkinter import font as tk_font
from typing import Any, Dict

from tknote.controller import Controller
from tknote.data.appstate_data import AppStateData
import tknote.defaults
from tknote.model import Model
from tknote.tk_geometry import TkGeometry
from tknote.utils import scalar_to_int


class App(tk.Tk):
    """
    The root application object. It extends
    :py:class:`tkinter.Tk`
    """
    def __init__(self):
        super().__init__()
        # create model
        self.model = Model()
        # retrieve app state from database
        self.state: AppStateData | None = self.model.read_app_state()
        # set initial windowsize early to prevent it from jumping.
        if self.state:
            self.geometry(self.state.window_geometry)
        self.title('TkNote')
        self.protocol('WM_DELETE_WINDOW', self.on_quit)
        self.minsize(650, 400)
        # set font
        self.event_add(
            '<<FontModified>>',
            'None'
        )
        self.font: tk_font.Font = tk_font.Font(
            family=getattr(self.state, 'app_font', 'Monaco'),
            name='AppFont',
            size=getattr(self.state, 'app_font_size', 12)
        )
        self.font_avg_chr_size = self.font.measure(
            "".join([chr(i) for i in range(128)])
        ) / 128
        # create view controller last
        self.controller = Controller(self, self.model)

    def set_font(
        self,
        font_name: str | None = None,
        font_size_scalar: float | None = None
    ):
        """
        Set the font for the application

        :param font_name: The name of the font family to set
        :type font_name: str or None
        :param font_size_scalar: A scalar value to set font size
        :type font_size_scalar: float or None

        """
        if font_name:
            self.font.configure(family=font_name)
        if font_size_scalar is not None:
            self.font.configure(
                size=scalar_to_int(
                    scalar=font_size_scalar,
                    min_val=tknote.defaults.FONT_MIN_SIZE,
                    max_val=tknote.defaults.FONT_MAX_SIZE
                )
            )
        self.font_avg_chr_size = self.font.measure(
            "".join([chr(i) for i in range(128)])
        ) / 128
        self.event_generate('<<FontModified>>')
        self.update_idletasks()

    def get_app_state(self) -> Dict[str, Any]:
        """
        Get the application state

        :return: The application's state
        :rtype: dict[str, :py:class:`typing.Any`]

        """
        win_geo = TkGeometry.from_str(self.geometry())
        controller = self.controller
        return {
            'window_width': win_geo.width,
            'window_height': win_geo.height,
            'window_x_offset': win_geo.x_off,
            'window_y_offset': win_geo.y_off,
            '_window_split_position': (
                str(controller.view.split_view.sash_coord(0))
            ),
            'list_index_selected': (
                self.model.selected_index
            ),
            'list_sort_key': (
                self.model.data_sort_key
            ),
            'list_sort_ascending': (
                int(self.model.data_sort_ascending)
            ),
            'app_font': self.font['family'],
            'app_font_size': self.font['size'],
        }

    def save_app_state(self):
        """
        Write the application state to the database

        """
        if self.state:
            self.state.__dict__.update(self.get_app_state())
            self.model.update_app_state(self.state)
        else:
            state_dict = self.get_app_state()
            state_dict['id_'] = None
            self.state = AppStateData(**state_dict)
            self.model.update_app_state(self.state)

    def on_quit(self):
        """
        Run on application quite to save app state and
        any unsaved user data, and permanently delete
        all notes marked for deletion.

        """
        # ensure all updates are written to database
        self.save_app_state()
        self.controller.on_quit()
        self.model.clean_deleted_notes()
        self.destroy()
