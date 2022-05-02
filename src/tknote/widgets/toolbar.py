"""
Toolbar Widget
"""
from __future__ import annotations

from abc import abstractmethod
import tkinter as tk
from tkinter import ttk

from tknote.widgets.widget_delegate import WidgetDelegate


class Toolbar(tk.Frame):  # pylint: disable=too-many-ancestors
    """
    A :py:mod:`tkinter` widget extending :py:class:`tkinter.Frame`
    to encapsulate the functionality of the application toolbar

    :param parent: The parent widget
    :type parent: :py:class:`tkinter.ttk.Frame`
    :param delegate: The `Toolbar` delegate
    :type delegate: :py:class:`.ToolbarDelegate`
    """
    def __init__(self, parent: ttk.Frame, delegate: ToolbarDelegate):
        super().__init__(parent)
        self.delegate: ToolbarDelegate = delegate
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.S, tk.E, tk.W)     # type: ignore
        )

        self.delete_button = tk.Button(self.button_frame, text='Delete')
        self.delete_button.pack(
            in_=self.button_frame,
            side=tk.LEFT,
            anchor=tk.W,
            padx=(10, 10),
            pady=(4, 8),
            expand=int(False)
        )
        self.create_button = tk.Button(self.button_frame, text='Create')
        self.create_button.pack(
            in_=self.button_frame,
            side=tk.LEFT,
            after=self.delete_button,
            anchor=tk.W,
            padx=(10, 10),
            pady=(4, 8),
            expand=int(False)
        )
        self.settings_button = tk.Button(
            self.button_frame,
            text='Settings'
        )
        self.settings_button.pack(
            in_=self.button_frame,
            side=tk.RIGHT,
            after=self.create_button,
            anchor=tk.E,
            padx=(10, 10),
            pady=(4, 8),
            expand=int(False)
        )

        self.rowconfigure(1, weight=0)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.separator.grid(
            column=0,
            row=1,
            sticky=(tk.N, tk.S, tk.E, tk.W)     # type: ignore
        )
        # add button callbacks
        self.delete_button.configure(
            command=self.delegate.delete_note
        )
        self.create_button.configure(
            command=self.delegate.create_note
        )
        self.settings_button.configure(
            command=self.delegate.display_settings
        )

    def disable_create(self):
        """
        Disable the toolbar's create button
        """
        self.create_button.configure(state='disable')

    def disable_delete(self):
        """
        Disable the toolbar's delete button
        """
        self.delete_button.configure(state='disable')

    def enable_create(self):
        """
        Enable the toolbar's create button
        """
        self.create_button.configure(state='normal')

    def enable_delete(self):
        """
        Enable the toolbar's delete button
        """
        self.delete_button.configure(state='normal')


class ToolbarDelegate(WidgetDelegate):
    """
    An abstract class extending
    :py:class:`tknote.widgets.widget_delegate.WidgetDelegate`
    that defines the delegate methods for :py:class:`.Toolbar`
    """

    @abstractmethod
    def delete_note(self):
        """
        Delegate method called when the toolbar's delete button
        is clicked

        :abstractmethod:
        """
        ...

    @abstractmethod
    def create_note(self):
        """
        Delegate method called when the toolbar's create button
        is clicked

        :abstractmethod:
        """
        ...

    @abstractmethod
    def display_settings(self):
        """
        Delegate method called when the toolbar's settings button
        is clicked

        :abstractmethod:
        """
        ...
