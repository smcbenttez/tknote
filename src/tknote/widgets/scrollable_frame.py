"""
ScrollableFrame Widget
"""
from __future__ import annotations

from sys import platform
import tkinter as tk
from tkinter import ttk
from typing import Callable

from tknote.tk_geometry import TkGeometry


class ScrollableFrame(tk.Frame):
    """
    An extension of :py:class:`tkinter.Frame` that adds
    scrolling functionality

    See :py:class:`tkinter.Frame` for details
    """
    def __init__(self, *args, **kwargs):
        class_ = kwargs.get('class_', 'ScrollableView')
        del kwargs['class_']
        super().__init__(class_=class_, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # TODO: fix mouse wheel scrolling
        self.canvas: tk.Canvas = tk.Canvas(self)
        self.canvas.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.S, tk.E, tk.W)     # type: ignore
        )
        self.canvas.columnconfigure(0, weight=1)
        self.canvas.rowconfigure(0, weight=1)
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self._scrollbar_modified
        )
        self.scrollbar.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.S)     # type: ignore
        )
        # TODO: find out why custom name isnt working.
        self.scrollview: tk.Frame = tk.Frame(
            self.canvas,
            class_='ScrollView',
        )
        self.scrollview.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.S, tk.E, tk.W)     # type: ignore
        )
        self.scrollview.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window(
            0,
            0,
            window=self.scrollview,
            anchor=(tk.NW)
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind(
            '<Configure>',
            self._canvas_modified
        )
        self.bind_all(
            '<<TkWorldChanged>>',
            self._app_updated
        )
        # mouse wheel scrolling
        self.bind_all(
            '<MouseWheel>',
            self._mouse_wheel_event
        )

    @property
    def gui_updated_callback(self) -> Callable:
        """
        Get and set the callback executed when the view is updated

        :type: :py:class:`typing.Callable`
        """
        return getattr(self, '_gui_updated_callback', lambda x: x)

    @gui_updated_callback.setter
    def gui_updated_callback(self, callback: Callable):
        self._gui_updated_callback = callback

    def _app_updated(self, _):
        """
        Callback used to updated the listview after the app
        is updated (such as changing the app font).
        """
        self.gui_updated_callback()

    def _canvas_modified(self, _):
        """
        Callback for when the canvas is modified.
        Calls method to update teh visible items.
        """
        self.gui_updated_callback()

    def _in_bounds(self, x: int, y: int) -> bool:
        bounds = TkGeometry.from_str(self.winfo_geometry())
        root_x = self.winfo_rootx()
        root_y = self.winfo_rooty()
        return (
            root_x <= x <= root_x + bounds.width
            and root_y <= y <= root_y + bounds.height
        )

    def _mouse_wheel_event(self, event: tk.Event):
        """
        Callback to intercept mouse wheel event to check
        if the mouse pointer was in the bounds of the
        `ScrollableFrame`
        """
        mouse_x = event.x_root
        mouse_y = event.y_root
        if platform == 'darwin':
            screen_units = event.delta * -1
        else:
            screen_units = event.delta
        if self._in_bounds(mouse_x, mouse_y):
            self.canvas.yview('scroll', screen_units, 'units')

    def _scrollbar_modified(self, *args):
        """
        Callback for when the scrollbar is moved or resized.
        Calls method to update the visible items.
        """
        self.canvas.yview(*args)
        self.gui_updated_callback()
