"""
Client to perform CRUD opertations on embedded sqlite database
"""
from dataclasses import asdict
import json
import sqlite3
from typing import List

from tknote.data.appstate_data import AppStateData
from tknote.data.note_data import NoteData


class NotesDB:
    """
    Sqlite database client

    :param path_to_db: Filepath to the sqlite databse
    :type path_to_db: str
    """
    def __init__(self, path_to_db: str) -> None:
        self.con = sqlite3.connect(path_to_db)
        self.con.row_factory = sqlite3.Row

    def __del__(self) -> None:
        self.con.close()

    def read_tables(self):
        """
        Get list of table names from database
        """
        result = self.con.execute(
            "SELECT * FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
        return [dict(row)['name'] for row in result]

    def create_appstate_table(self):
        # TODO: Need to create vec2 type and translator for sqlite
        """
        Create `appstate` table in the database
        """
        self.con.execute(
            '''
            CREATE TABLE appstate
                (
                    id_ INTEGER PRIMARY KEY AUTOINCREMENT,
                    window_width INTEGER,
                    window_height INTEGER,
                    window_x_offset INTEGER,
                    window_y_offset INTEGER,
                    _window_split_position TEXT,
                    list_index_selected INT,
                    list_sort_key TEXT,
                    list_sort_ascending INTEGER,
                    app_font TEXT,
                    app_font_size INTEGER
                )
            '''
        )
        self.con.commit()

    def create_appstate(self, app_state: AppStateData) -> int:
        """
        Insert app state into the database

        :param app_state: The application state
        :type app_state:
            :py:class:`tknote.data.appstate_data.AppStateData`
        :return: The database row ID for the row inserted
        :rtype: int
        """
        cursor = self.con.cursor()
        cursor.execute(
            """
            INSERT INTO appstate VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            app_state.as_tuple
        )
        new_id = cursor.lastrowid
        self.con.commit()
        return new_id

    def read_appstate(self) -> AppStateData | None:
        """
        Get the saved application state

        :return: An application state if it exits in the database
        :rtype: :py:class:`tknote.data.appstate_data.AppStateData`
            or :py:class:`None`
        """
        result = self.con.execute(
            "SELECT * FROM appstate"
        ).fetchone()
        if result:
            return AppStateData(**dict(result))
        return None

    def update_appstate(self, app_state: AppStateData):
        """
        Update database with provided applicatoin state

        :param app_state: The application state
        :type app_state:
            :py:class:`tknote.data.appstate_data.AppStateData`
        """
        self.con.execute(
            """
            UPDATE appstate
            SET
                window_width = ?,
                window_height = ?,
                window_x_offset = ?,
                window_y_offset = ?,
                _window_split_position = ?,
                list_index_selected = ?,
                list_sort_key = ?,
                list_sort_ascending = ?,
                app_font = ?,
                app_font_size = ?
            WHERE id_ = ?
            """,
            tuple(
                v for k, v in asdict(app_state).items()
                if not k.endswith('_')
            ) + (app_state.id_,)
        )
        self.con.commit()

    def delete_appstate(self, app_state: AppStateData):
        """
        Delete row in database corresponding to provided
        AppStateData object

        :param app_state: The application state
        :type app_state:
            :py:class:`tknote.data.appstate_data.AppStateData`
        """
        self.con.execute(
            """
            DELETE FROM appstate WHERE id_ = ?
            """,
            (app_state.id_,)
        )
        self.con.commit()

    def create_notes_table(self) -> None:
        """
        Create `notes` table in database
        """
        self.con.execute(
            '''
            CREATE TABLE notes
                (
                    _id INTEGER PRIMARY KEY AUTOINCREMENT,
                    _deleted INTEGER,
                    _time_created INTEGER,
                    _time_edited INTEGER,
                    _text TEXT
                )
            '''
        )
        self.con.commit()

    def create_note(self, note: NoteData) -> int:
        """
        Insert note into the database

        :param note: Note to insert into database
        :type note: :py:class:`tknote.data.note_data.NoteData`
        :return: The database row ID for the row inserted
        :rtype: int
        """
        cursor = self.con.cursor()
        cursor.execute(
            "INSERT INTO notes VALUES (?, ?, ?, ?, ?)",
            note.as_tuple
        )
        new_id = cursor.lastrowid
        self.con.commit()
        return new_id

    def create_notes(self, notes: List[NoteData]) -> list[int]:
        """
        Insert notes into the database

        :param notes: Notes to insert into the database
        :type notes: list[:py:class:`tknote.data.note_data.NoteData`]
        :return: The database row IDs for the rows inserted
        :rtype: list[int]
        """
        return [self.create_note(note) for note in notes]

    def read_notes(self) -> List[NoteData]:
        """
        Get all notes from the database
        """
        result = self.con.execute(
            "SELECT * FROM notes"
        )
        return [NoteData(**dict(x)) for x in result]

    def update_note(self, note: NoteData):
        """
        Update row in database corresponding to provided note

        :param note: Note to update in database
        :type note: :py:class:`tknote.data.note_data.NoteData`
        """
        self.con.execute(
            """
            UPDATE notes
            SET _deleted=?, _time_edited = ?, _text = ?
            WHERE _id = ?
            """,
            (note.deleted, note.time_edited, note.text, note.db_id)
        )
        self.con.commit()

    def update_notes(self, notes: List[NoteData]):
        """
        Update rows in database corresponding to provided notes

        :param notes: Notes to update in database
        :type notes: list[:py:class:`tknote.data.note_data.NoteData`]
        """
        for note in notes:
            self.update_note(note)

    def delete_notes_marked_for_deletion(self):
        """
        Delete notes from database marked as deleted
        """
        self.con.execute(
            """
            DELETE FROM notes
            WHERE _deleted = 1
            """
        )
        self.con.commit()

    def delete_note(self, note: NoteData):
        """
        Delete note from database corresponding to provided note

        :param note: The note to delete
        :type note: :py:class:`tknote.data.note_data.NoteData`
        """
        self.con.execute(
            """
            DELETE FROM notes
            WHERE _id = ?
            """,
            (note.db_id,)
        )
        self.con.commit()

    def delete_notes(self, notes: List[NoteData]):
        """
        Delete notes from database corresponding to provided notes

        :param notes: The notes to delete
        :type notes: list[:py:class:`tknote.data.note_data.NoteData`]
        """
        for note in notes:
            self.delete_note(note)

    @staticmethod
    def row_to_json(row_data: sqlite3.Row):
        """
        Convert row in database to json

        :param row_data: The database row
        :type row_data: :py:class:`sqlite3.Row`
        """
        return json.dumps(dict(row_data))
