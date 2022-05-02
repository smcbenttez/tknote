"""
Application Model
"""
from typing import Any, Dict

from tknote.data.appstate_data import AppStateData
from tknote.data.note_data import NoteData
from tknote.data.setting_data import SettingData
from tknote.db import NotesDB
from tknote.observable_types import (
    observable,
    ObservableList,
    ObservableMixin
)


@observable(['data_time_key', 'selected_index'])
class Model(ObservableMixin):
    """
    The application model. An extension of
    of :py:class:`tknote.observable_types.ObservableMixin`
    and decorated by :py:func:`tknote.observable_types.observable`.
    """
    def __init__(self):
        """
        Constructor method
        """
        self._data: ObservableList[NoteData]
        self._data_sort_ascending: int
        self._data_sort_key: str
        self._data_time_key: str
        self._db_con: NotesDB
        self._selected_index: int | None
        self.settings: Dict[str, SettingData]
        self.state: AppStateData

        self._db_con = NotesDB('notes.db')
        # check for existing db tables
        tables = self._db_con.read_tables()
        if 'notes' not in tables:
            self._db_con.create_notes_table()
        if 'appstate' not in tables:
            self._db_con.create_appstate_table()

        self._data = ObservableList()
        self._deleted_notes = []

    @property
    def data_sort_ascending(self) -> bool:
        """
        Get and set whether or not the model's data is sorted
        in ascending order

        :type: bool
        """
        return getattr(self, '_data_sort_ascending', False)

    @data_sort_ascending.setter
    def data_sort_ascending(self, sort_ascending: bool | int):
        if isinstance(sort_ascending, bool):
            self._data_sort_ascending = sort_ascending
        else:
            self._data_sort_ascending = bool(sort_ascending)
        self.sort_data()

    @property
    def data_sort_key(self) -> str:
        """
        Get and set the key used for sorting the model's data

        :type: str
        """
        return getattr(self, '_data_sort_key', '')

    @data_sort_key.setter
    def data_sort_key(self, key: str):
        if key in ('time_created', 'time_edited'):
            self.data_time_key = key
        else:
            self.data_time_key = 'time_edited'
        self._data_sort_key = key
        self.sort_data()

    @property
    def data_time_key(self) -> str:
        """
        Get and set the name of the time attribute currently
        used by the application to sort and display data

        :type: str
        """
        return getattr(self, '_data_time_key')

    @data_time_key.setter
    def data_time_key(self, key: str):
        self._data_time_key = key

    @property
    def last_deleted_note(self) -> NoteData | None:
        """
        Get the most recently deleted note

        :type: :py:class:`tknote.data.note_data.NoteData` or None
        """
        if self._deleted_notes:
            return self._deleted_notes[-1]
        return None

    @property
    def notes(self) -> ObservableList[NoteData]:
        """
        Get the application's list of notes

        :type: :class:`tknote.observable_types.ObservableList`
            [:class:`tknote.data.note_data.NoteData`]
        """
        return self._data

    @property
    def selected_note(self) -> NoteData | None:
        """
        Get the current selected note

        :type: :py:class:`tknote.data.note_data.NoteData` or None
        """
        if self.selected_index is not None:
            return self.notes[self.selected_index]
        return None

    @property
    def selected_index(self) -> int | None:
        """
        Get or set the currently list index

        :type: int or None
        """
        return (
            getattr(self, '_selected_index', None)
        )

    @selected_index.setter
    def selected_index(self, index: int | None):
        self._selected_index = index

    @property
    def state(self) -> Dict[str, Any]:
        """
        Get the model's current state

        :type: dict[str, :py:class:`typing.Any`]
        """
        return {
            'list_index_selected': self.selected_index,
            'settings': [(k, v.value) for k, v in self.settings.items()]
        }

    def add_setting(self, setting: SettingData):
        """
        Add a setting to the application's settings

        :param setting: The setting to add
        :type setting: :py:class:`tknote.data.setting_data.SettingData`
        :raises ValueError: if attemping to add a setting with the
            same name as an existing setting
        """
        if self.settings.get(setting.name, False):
            raise ValueError(
                f"Setting by the name of '{setting.name}' already exists."
            )
        self.settings[setting.name] = setting

    def append_note(self, note: NoteData):
        """
        Append a note to the model's list of notes

        :param note: The note to append
        :type note: :py:class:`tknote.data.note_data.NoteData`
        """
        self.notes.append(note)

    def clean_deleted_notes(self):
        """
        Permanently delete all notes marked for deletion from
        the database
        """
        self._db_con.delete_notes_marked_for_deletion()

    def create_note(self):
        """
        Create a new note and insert it into the model's
        list of notes
        """
        new_note = NoteData.new()
        new_note.db_id = self._db_con.create_note(new_note)
        self.notes.insert(0, new_note)
        if self.selected_index is not None:
            self.selected_index += 1

    def delete_note(self, index: int):
        """
        Delete a note from the model's list of notes at the
        specified index

        :param index: The index of the note to delete
        :type index: int
        """
        # remove from list
        note_to_delete: NoteData = self.notes.pop(index)
        # mark as deleted in db
        note_to_delete.deleted = True
        # immediately delete note from db if empty
        if note_to_delete.is_empty:
            self._db_con.delete_note(note_to_delete)
            return
        self._db_con.update_note(note_to_delete)
        # add to _deleted_notes for undo functionality
        note_to_delete.clear_callbacks()
        self._deleted_notes.append(note_to_delete)

    def get_notes(self):
        """
        Get all notes from the database and insert them
        into the model's list of notes
        """
        notes = sorted(
            self._db_con.read_notes(),
            key=lambda x: getattr(x, self.data_sort_key),
            reverse=not self.data_sort_ascending
        )
        for note in notes:
            self.notes.insert(len(self.notes), note)

    def get_setting_value(self, setting_name: str) -> Any:
        """
        Get the value for the specified setting

        :param setting_name: The name of the setting
        :type setting_name: str
        :return: The setting's value
        :rtype: :py:class:`typing.Any`
        :raises ValueError: if the setting by the name of
            `setting_name` does not exist
        """
        if not self.settings.get(setting_name, False):
            raise ValueError(
                f"Setting by the name of '{setting_name}' does not exist."
            )
        # ignore type because mypy does not recognize this unpacking.
        return self.settings.get(setting_name).value    # type: ignore

    def insert_note(self, note: NoteData):
        """
        Insert note into the model's list of notes at the
        appropriate index according the existing sort configuration

        :param note: The note to insert
        :type note: :py:class:`tknote.data.note_data.NoteData`
        """
        sort_key_values = [
            getattr(note, self.data_sort_key) for note in self.notes
        ]
        sort_key_values.append(getattr(note, self.data_sort_key))
        note_index = len(sort_key_values) - 1
        sort_order, _ = zip(*sorted(
            enumerate(sort_key_values),
            key=lambda x: x[1],
            reverse=not self.data_sort_ascending
        ))
        new_index = sort_order.index(note_index)
        self.notes.insert(new_index, note)
        if self.selected_index is None:
            self.selected_index = 0
        else:
            if new_index <= self.selected_index:
                self.selected_index += 1

    def read_app_state(self) -> AppStateData | None:
        """
        Get the application state that has been saved in
        the database

        :return: The saved application state
        :rtype: :py:class:`tknote.data.appstate_data.AppStateData`
        """
        return self._db_con.read_appstate()

    def set_setting_value(self, setting_name: str, value: Any):
        """
        Set a setting's value

        :param setting_name: The name of the setting to set the
            value for
        :type setting_name: str
        :param value: The value to set
        :type value: :py:class:`typing.Any`
        :raises ValueError: if the setting by the name of `setting_name`
            does not exist
        """
        if not self.settings.get(setting_name, False):
            raise ValueError(
                f"Setting by the name of `{setting_name}` does not exist."
            )
        # ignore type because mypy does not recognize this unpacking.
        self.settings.get(setting_name).value = value   # type: ignore

    def set_data_sort_key(self, sort_key: str):
        """
        Callback to set :py:attr:`tknote.model.Model.data_sort_key`
        from a user readable string

        :param sort_key: The key to be used to sort the data
        :type sort_key: str
        """
        self.data_sort_key = "_".join(sort_key.split(" ")).lower()

    def set_data_sort_order(self, sort_order: str):
        """
        Callback to set :py:attr:`tknote.model.Model.data_sort_order`
        from a user readable string

        :param sort_order: Either 'Ascending' or 'Descending'
        :type sort_order: str
        """
        if sort_order == 'Ascending':
            self.data_sort_ascending = True
        else:
            self.data_sort_ascending = False

    def sort_data(self):
        """
        Sort the model's data in place according to
        :py:attr:`tknote.model.Model.data_sort_key`
        and :py:attr:`tknote.model.Model.data_sort_ascending`
        """
        sort_order = self.notes.sort(
            key=lambda x: getattr(x, self.data_sort_key),
            reverse=not self.data_sort_ascending
        )
        if self.selected_index in sort_order:
            self.selected_index = sort_order.index(self.selected_index)
        else:
            self.selected_index = None

    def undo_delete_note(self):
        """
        Undo the deletion of the most recently deleted note
        """
        if not self._deleted_notes:
            return
        note_to_restore = self._deleted_notes.pop()
        note_to_restore.deleted = False
        self._db_con.update_note(note_to_restore)
        self.insert_note(note_to_restore)

    def update_app_state(self, app_state: AppStateData):
        """
        Update the database with the provided application state

        :param app_state: The app state
        :type app_state:
            :py:class:`tknote.data.appstate_data.AppStateData`
        """
        if app_state.db_id:
            self._db_con.update_appstate(app_state)
        else:
            new_id = self._db_con.create_appstate(app_state)
            app_state.db_id = new_id

    def update_note_text(self, note: NoteData, text: str):
        """
        Update the note's corresponding database entry

        :param note: The note to update
        :type note: :py:class:`tknote.data.note_data.NoteData`
        :param text: The updated note text
        :type text: str
        """
        note.text = text
        self._db_con.update_note(note)
        self.sort_data()
