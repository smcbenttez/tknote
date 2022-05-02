"""
Controller Class
"""
from __future__ import annotations

from sys import platform
import tkinter as tk
from typing import TYPE_CHECKING

from tknote.data.note_data import NoteData
import tknote.defaults
from tknote.model import Model
from tknote.settings_controller import SettingsController
from tknote.widgets.animated_list import ListDelegate
from tknote.widgets.note_editor import NoteEditorDelegate
from tknote.widgets.note_list_item import NoteListItem
from tknote.widgets.toolbar import ToolbarDelegate
from tknote.utils import strip_extra_whitespace
from tknote.view import View
from tknote.utils import clip_value

if TYPE_CHECKING:
    from tkinter import font as tk_font
    from tknote.app import App
    from tknote.observable_types import CallbackData, ObservableList


class Controller(ListDelegate, NoteEditorDelegate, ToolbarDelegate):
    """
    The application controller. It is an extended combination
    of the :py:class:`tknote.widgets.animated_list.ListDelegate`,
    :py:class:`tknote.widgets.note_editor.NoteEditorDelegate`, and
    :py:class:`tknote.widgets.toolbar.ToolbarDelegate` clases

    :param app_root: The application root object
    :type app_root: :py:class:`tknote.main.App`
    :param app_model: The application model object
    :type app_model: :py:class:`tknote.model.Model`
    """
    def __init__(self, app_root: App, app_model: Model):
        self.app = app_root
        self.settings_controller: SettingsController | None = (
            None
        )
        # data model
        self.model: Model = app_model
        self.model.data_sort_ascending = getattr(
            self.app.state,
            'list_sort_ascending',
            tknote.defaults.SORT_ASCENDING
        )
        self.model.data_sort_key = getattr(
            self.app.state,
            'list_sort_key',
            tknote.defaults.SORT_KEY
        )
        # add callbacks to model data
        # TODO: move this into method?
        self.model.notes.add_callback(
            'append', self.append_new_note_list_item
        )
        self.model.notes.add_callback(
            'insert', self.insert_new_note_list_item
        )
        # bind event
        mod_key = 'Control'
        if platform == 'darwin':
            mod_key = 'Command'
        self.app.bind_all(
            f'<{mod_key}-z>',
            self.undo_note_delete
        )
        # create virtual events
        self.app.event_add(
            '<<ListItemSelected>>',
            'None'
        )
        self.app.event_add(
            '<<ListItemDeselected>>',
            'None'
        )
        self.app.event_add(
            '<<ListItemSizeModified>>',
            'None'
        )
        self.app.event_add(
            '<<NoteTextUpdated>>',
            'None'
        )
        # create view
        self.view = View(
            app_root=self.app,
            list_delegate=self,
            note_editor_delegate=self,
            toolbar_delegate=self
        )
        # set window split position
        if self.app.state:
            sash_coords = self.app.state.window_split_position
            self.view.split_view.sash_place(0, *sash_coords)
        self.view.update()
        # populate model with data
        self.model.get_notes()
        self.select_list_index(
            getattr(
                self.app.state,
                'list_index_selected',
                None
            )
        )
        if not self.model.notes:
            self.create_note()
        # self.select_list_index(self.model.selected_index)

    # callbacks to add to model.data
    def create_note_list_item(self, note: NoteData) -> NoteListItem:
        """
        Creates an instance of
        :py:class:`tknote.widgets.note_list_item.NoteListItem`

        :param note: The corresponding note data
        :type note: :py:class:`tknote.data.note_data.NoteData`
        :return: A new `NoteListItem`
        :rtype: :py:class:`tknote.widgets.note_list_item.NoteListItem`
        """
        new_item = NoteListItem(
            self.view.note_list,
            note
        )
        return new_item

    def insert_note_list_item(self, at_index: int, item: NoteListItem):
        """
        Inserts a :py:class:`tknote.widgets.note_list_item.NoteListItem`
        into the application's
        :py:class:`tknote.widgets.animated_list.AnimatedList`.

        :param at_index: The list index where to insert the item
        :type at_index: int
        :param item: The `NoteListItem` to insert
        :type item:
            :py:class:`tknote.widgets.note_list_item.NoteListItem`
        """
        self.view.note_list.items.insert(at_index, item)

    def insert_new_note_list_item(self, data: CallbackData):
        """
        Callback used to insert a
        :py:class:`tknote.widgets.note_list_item.NoteListItem` into
        the application's `AnimatedList`. Not intended to be called
        directly

        :param data: Data from the object executing the callback
        :type data: :py:class:`tknote.observable_types.CallbackData`
        """
        self.insert_note_list_item(
            data.input_data[0],
            self.create_note_list_item(data.input_data[1])
        )

    def append_new_note_list_item(self, data: CallbackData):
        """
        Callback used to append a
        :py:class:`tknote.widgets.note_list_item.NoteListItem` into
        the application's `AnimatedList`. Not intended to be called
        directly

        :param data: Data from the object executing the callback
        :type data: :py:class:`tknote.observable_types.CallbackData`
        """
        self.insert_note_list_item(
            len(self.model.notes),
            self.create_note_list_item(data.input_data[0])
        )

    def deselect_list_index(self, index: int | None):
        """
        Deselect item at provided index in application's `AnimatedList`

        :param index: List index to deselect
        :type index: int or None
        """
        if not self.model.notes:
            return
        if index is None:
            return
        self.view.note_list.items[index].deselect()
        self.model.selected_index = None
        self.view.note_list.event_generate(
            '<<ListItemDeselected>>'
        )

    def select_list_index(self, index: int | None):
        """
        Select item at provided index in application's `AnimatedList`

        :param index: List index to select
        :type index: int or None
        """
        if not self.model.notes:
            return
        # select first item if index is None
        if index is None:
            index = 0
        if index == self.model.selected_index:
            return
        self.view.note_list.items[index].select()
        self.model.selected_index = index
        # make sure selected item is visible
        self.view.note_list.scroll_to_item(
            self.view.note_list.items[index]
        )
        tk.Event.VirtualEventData = (   # type: ignore
            self.model.selected_note
        )
        self.view.note_list.event_generate(
            '<<ListItemSelected>>'
        )

    def undo_note_delete(self, _):
        """
        Callback used to undo the deletion of a note

        :param _: Unused parameter
        """
        if (
            (not self.view.note_editor.can_undo)
            and self.model.last_deleted_note
        ):
            self.model.undo_delete_note()

    # NoteEditorDelegate methods
    def note_deselected(self, event: tk.Event):
        """
        Delegate method for
        :py:class:`tknote.widgets.note_editor.NoteEditor`.
        Executed when a note is deselected.

        :param event: The event data
        :type event: :py:class:`tkinter.Event`
        """
        self.view.note_editor.clear_text()
        self.view.note_editor.disabled = True

    def note_selected(self, event: tk.Event):
        """
        Delegate method for
        :py:class:`tknote.widgets.note_editor.NoteEditor`.
        Executed when a note is selected.

        :param event: The event data
        :type event: :py:class:`tkinter.Event`
        """
        self.view.note_editor.disabled = False
        self.view.note_editor.update_text(
            event.VirtualEventData.text     # type: ignore
        )
        self.view.note_editor.reset_undo_stack()

    def text_updated(self, event: tk.Event):
        """
        Delegate method for
        :py:class:`tknote.widgets.note_editor.NoteEditor`.
        Executed when the text in the editor is updated

        :param event: The event data
        :type event: :py:class:`tkinter.Event`
        """
        if not self.model.notes:
            return
        if not self.model.selected_note:
            return
        updated_text = event.widget.get('1.0', 'end')
        # check to see if the text was updated or a new item was selected
        # strip last character because Tk adds a newline
        if self.model.selected_note.text == updated_text[:-1]:
            return
        stripped_text = strip_extra_whitespace(updated_text)
        if stripped_text:
            self.view.toolbar.enable_create()
        else:
            self.view.toolbar.disable_create()
        self.model.update_note_text(
            self.model.selected_note, stripped_text
        )

    # ToolbarDelegate methods
    def create_note(self):
        """
        Delegate method for
        :py:class:`tknote.widgets.toolbar.Toolbar`.
        Executed when the 'create new note' button is
        pressed to create a new note

        :param event: The event data
        :type event: :py:class:`tkinter.Event`
        """
        self.model.create_note()
        self.deselect_list_index(self.model.selected_index)
        self.select_list_index(0)
        self.view.toolbar.enable_delete()
        self.view.toolbar.disable_create()

    def delete_note(self):
        """
        Delegate method for
        :py:class:`tknote.widgets.toolbar.Toolbar`.
        Executed when the 'delete note' button is
        pressed to delete the selected note

        :param event: The event data
        :type event: :py:class:`tkinter.Event`
        """
        if not self.model.notes:
            return
        note_index = self.model.selected_index
        self.deselect_list_index(note_index)
        self.model.delete_note(note_index)
        # enable create button
        self.view.toolbar.enable_create()
        # adjust selected_index if last note is deleted
        if not self.model.notes:
            self.model.selected_index = None
            self.view.toolbar.disable_delete()
            return
        self.select_list_index(
            clip_value(
                note_index,
                0,
                len(self.model.notes) - 1
            )
        )

    def display_settings(self):
        """
        Delegate method for
        :class:`tknote.widgets.toolbar.Toolbar`.
        Executed when the "settings" button is
        pressed to display the settings window
        """
        # only allow one settings window open at a time
        if self.settings_controller:
            self.settings_controller.settings_window.focus()
        else:
            self.settings_controller = SettingsController(
                self.app
            )

    # ListDelegate methods
    @property
    def list_data(self) -> ObservableList:
        """
        Get backing data for `AnimatedList`. Delegate property for
        :py:class:`tknote.widgets.animated_list.AnimatedList`.

        :return: The list of notes in the application model
        :rtype: :py:class:`tknote.observable_types.ObservableList`
        """
        return self.model.notes

    def list_index_selected(self, index_selected: int):
        """
        Delegate property for
        :py:class:`tknote.widgets.animated_list.AnimatedList`.
        Executed when a `ListItem` in the `AnimatedList` is
        selected

        :param index_selected: The index in the list of item selected
        :type index_selected: int
        """
        if index_selected == self.model.selected_index:
            return
        # delete note if empty when navigating away
        note_deleted: bool = False
        if self.model.selected_note:
            if self.model.selected_note.is_empty:
                self.delete_note()
                note_deleted = True
        # modify index_selected if a note was deleted
        if note_deleted and self.model.selected_index is not None:
            if index_selected > self.model.selected_index:
                index_selected -= 1
        # select ui list item
        if index_selected == self.model.selected_index:
            return
        self.deselect_list_index(self.model.selected_index)
        self.select_list_index(index_selected)

    # WidgetDelegate methods
    @property
    def font(self) -> tk_font.Font:
        """
        Get the application font. Delegate property for
        :py:class:`tknote.widgets.widget_delegate.WidgetDelegate`.
        Used to access the application font

        :return: The application font
        :rtype: :py:class:`tkinter.font.Font`
        """
        return self.app.font

    def on_quit(self):
        """
        Called when the appliation is quit
        """
        if self.model.selected_note:
            if self.model.selected_note.is_empty:
                self.delete_note()
