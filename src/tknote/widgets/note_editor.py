"""
NoteEditor Widget
"""
from __future__ import annotations

from abc import abstractmethod
import tkinter as tk

from tknote.widgets.widget_delegate import WidgetDelegate


class NoteEditor(tk.Frame):    # pylint: disable=too-many-ancestors
    """
    A :py:mod:`tkinter` widget that extends :py:class:`tkinter.Frame`

    :param delegate: The delegate for the :py:class:`.NoteEditor`
    :type delegate: :py:class:`.NoteEditorDelegate`
    """
    def __init__(self, delegate: NoteEditorDelegate, *args, **kwargs):
        super().__init__(class_='NoteEditor', *args, **kwargs)
        self._can_undo: bool = False
        # delegate
        self._delegate: NoteEditorDelegate = delegate
        # configure
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.W, tk.E, tk.S)     # type: ignore
        )
        self.text_editor = tk.Text(self, font=self.delegate.font)
        self.text_editor.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.W, tk.E, tk.S)     # type: ignore
        )
        self.text_editor.configure(
            highlightthickness=0,
            wrap=tk.WORD,
            undo=True
        )
        # events
        self.bind_all(
            '<<ListItemSelected>>',
            self.delegate.note_selected
        )
        self.bind_all(
            '<<ListItemDeselected>>',
            self.delegate.note_deselected
        )
        self.bind_all(
            '<<NoteTextUpdated>>',
            self.delegate.text_updated
        )
        self.text_editor.bind(
            '<<UndoStack>>',
            self.undo_stack_modified
        )

        # setup polling to check for changes to text
        self.after(33, self.check_for_updates)

    @property
    def can_undo(self) -> bool:
        """
        Get whether or not there are edits that can be undone

        :type: bool
        """
        return self._can_undo

    @property
    def delegate(self) -> NoteEditorDelegate:
        """
        Get and set the delegate

        :type: :py:class:`.NoteEditorDelegate`
        """
        return self._delegate

    @delegate.setter
    def delegate(self, delegate: NoteEditorDelegate):
        self._delegate = delegate

    @property
    def disabled(self) -> bool:
        """
        Get and set whether or not the `NoteEditor` is disabled

        :type: bool
        """
        return self.text_editor.cget('state') == 'disabled'

    @disabled.setter
    def disabled(self, disable: bool):
        if disable:
            state = 'disabled'
        else:
            state = 'normal'
        self.text_editor.configure(state=state)     # type: ignore

    def check_for_updates(self):
        """
        Check for updates to the text in the editor
        """
        # TODO: there must be a better way
        if self.text_editor.edit_modified():
            self.text_editor.event_generate(
                '<<NoteTextUpdated>>'
            )
            self.text_editor.edit_modified(False)
        # TODO: using after_idle locks the app up.. need to debug
        self.after(33, self.check_for_updates)

    def clear_text(self):
        """
        Clear the text in the editor
        """
        self.text_editor.delete('1.0', 'end')

    def reset_undo_stack(self):
        """
        Reset the editor's undo stack
        """
        self.text_editor.edit_reset()

    def undo_stack_modified(self, _):
        """
        Callback to track the state of the editor's undo stack

        :param _: Unused parameter
        """
        self._can_undo = self.text_editor.edit('canundo')

    def update_text(self, text: str):
        """
        Update text in the editor

        :param text: The text to update the editor
        :type text: str
        """
        self.text_editor.insert('end', text)


class NoteEditorDelegate(WidgetDelegate):
    """
    Abstract class that extends
    :py:class:`tknote.widget.widget_delegage.WidgetDelegate`
    to define the required delegate methods for
    :py:class:`.NoteEditor`
    """

    @abstractmethod
    def note_deselected(self, event: tk.Event):
        """
        Delegate method called when a note is deselected

        :abstractmethod:
        :param event: The event data
        :type event: :py:class:`tkinter.Event`
        """
        ...

    @abstractmethod
    def note_selected(self, event: tk.Event):
        """
        Delegate method called when a note is selected

        :abstractmethod:
        :param event: The event data
        :type event: :py:class:`tkinter.Event`
        """
        ...

    @abstractmethod
    def text_updated(self, event: tk.Event):
        """
        Delegate method called when the editor's text is updated

        :abstractmethod:
        :param event: The event data
        :type event: :py:class:`tkinter.Event`
        """
        ...
