"""
View Class
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from tknote.animation.animation_manager import AnimationManager
from tknote.widgets.animated_list import AnimatedList
from tknote.widgets.note_editor import NoteEditor
from tknote.widgets.toolbar import Toolbar

if TYPE_CHECKING:
    from tknote.widgets.animated_list import ListDelegate
    from tknote.widgets.note_editor import NoteEditorDelegate
    from tknote.widgets.toolbar import ToolbarDelegate


class View(ttk.Frame):      # pylint: disable=too-many-ancestors
    """
    The application's main view. `View` is an extension of
    :py:class:`tkinter.ttk.Frame`

    :param app_root: The application's root object
    :type app_root: :py:class:`tkinter.Tk`
    :param list_delegate: The delegate for the view's list
        (:py:class:`tknote.widgets.animated_list.AnimatedList`)
    :type list_delegate:
        :py:class:`tknote.widgets.animated_list.ListDelegate`
    :param note_editor_delegate: The delegate for the note editor
        (:py:class:`tknote.widgets.note_editor.NoteEditor`)
    :type note_editor_delegate:
        :py:class:`tknote.widgets.note_editor.NoteEditorDelegate`
    :param toolbar_delegate: The delegate for the view's toolbar
        (:py:class:`tknote.widgets.toolbar.Toolbar`)
    :type toolbar_delegate:
        :py:class:`tknote.widgets.toolbar.ToolbarDelegate`
    """
    def __init__(
        self,
        app_root: tk.Tk,
        list_delegate: ListDelegate,
        note_editor_delegate: NoteEditorDelegate,
        toolbar_delegate: ToolbarDelegate
    ):
        super().__init__(app_root, padding=(0, 0, 0, 0))
        self.root = app_root
        # root layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.W, tk.E, tk.S)    # type: ignore
        )
        self.toolbar = Toolbar(self, toolbar_delegate)
        self.toolbar.grid(
            column=0,
            row=0,
            sticky=(tk.E, tk.W)     # type: ignore
        )

        # split view
        self.rowconfigure(1, weight=1)
        self.split_view = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=5
        )
        self.split_view.grid(
            column=0,
            row=1,
            sticky=(tk.N, tk.W, tk.E, tk.S)     # type: ignore
        )

        # list view
        self.note_list = AnimatedList(
            animation_manager=AnimationManager(app_root),
            delegate=list_delegate
        )

        # text editor
        self.note_editor = NoteEditor(delegate=note_editor_delegate)

        # add widgets to paned window
        self.split_view.add(
            self.note_list,
            sticky=(tk.N, tk.S, tk.E, tk.W),
            minsize=250,
            width=250,
            stretch='never',
        )
        self.split_view.add(
            self.note_editor,
            after=self.note_list,
            sticky=(tk.N, tk.S, tk.E, tk.W),
            minsize=400,
            width=400,
            height=400,
            stretch='always',
        )
