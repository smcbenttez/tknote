"""
NoteData Class
"""
from __future__ import annotations

from dataclasses import asdict, astuple, dataclass
import time
from typing import Tuple

from tknote.observable_types import observable, ObservableMixin
from tknote.utils import strip_extra_whitespace


@dataclass(init=False, repr=False, kw_only=True)
@observable(['text'])
class NoteData(ObservableMixin):
    """
    An extension of :py:class:`tknote.observable_types.ObservableMixin`
    decorated with :py:func:`dataclasses.dataclass` and
    :py:func:`tknote.observable_types.observable` that
    encapsulates the note data

    All instance variables are private and have
    associated getter and setters provided via Python
    `property` decorated methods. This allows for
    properties to be wrapped with callback execution
    to create to "observable" version.

    Use Note classmethod `new` to create a new
    instance of Note.

    :param _id: the database id
    :type _id: int or None
    :param _deleted: 0 or 1 representing whether or not the
        note has been marked for deletion
    :type _deleted: int
    :param _time_created: Unix timestamp corresponding to the
        note's time of creation
    :type _time_created: float
    :param _time_edited: Unix timestamp corresponding to the note's
        most recent edit
    :type _time_edited: float
    :param _text: The note's text
    :type: _text: str
    """
    _id: int | None
    _deleted: int
    _time_created: float
    _time_edited: float
    _text: str

    def __init__(
        self,
        /,
        _id,
        _deleted,
        _time_created,
        _time_edited,
        _text
    ):
        self._id = _id
        self._deleted = _deleted
        self._time_created = _time_created
        self._time_edited = _time_edited
        self._text = _text

    def __repr__(self):
        return str(asdict(self))

    @classmethod
    def new(cls, /, text: str = "") -> NoteData:
        """
        Create a new instance of `NoteData`

        :param text: The note's text
        :type text: str
        """
        now = time.time()
        return cls(
            _id=None,
            _deleted=0,
            _time_created=now,
            _time_edited=now,
            _text=text
        )

    @property
    def as_tuple(self) -> Tuple:
        """
        Get the note's data packed into a tuple

        :type: tuple
        """
        return astuple(self)

    @property
    def db_id(self) -> int | None:
        """
        Get and set the note's database id

        :type: int or None
        """
        return self._id

    @db_id.setter
    def db_id(self, db_id: int):
        self._id = db_id

    @property
    def deleted(self) -> bool:
        """
        Get and set whether or not the note is marked for deletion

        :type: bool
        """
        return bool(self._deleted)

    @deleted.setter
    def deleted(self, delete_bool):
        self._deleted = int(delete_bool)

    @property
    def is_empty(self) -> bool:
        """
        Get whether or not the note's text is an empty string

        :type: bool
        """
        if not self.text:
            return True
        return False

    @property
    def preview(self) -> str:
        """
        Get the note's second line of text

        :type: str
        """
        return self._get_line(2)

    @property
    def text(self) -> str:
        """
        Get and set the note's text. Autmatically updates the
        time of the note's last edit

        :type: str
        """
        return self._text

    @text.setter
    def text(self, updated_text: str):
        self._text = updated_text
        # update the time of the last edit
        self._time_edited = time.time()

    @property
    def time_created(self) -> float:
        """
        Get the time the note was created

        :type: float
        """
        return self._time_created

    @property
    def time_edited(self) -> float:
        """
        Get the time the note was last edited

        :type: float
        """
        return self._time_edited

    @property
    def title(self) -> str:
        """
        Get the note's first line

        :type: str
        """
        return self._get_line(1)

    def _get_line(self, line_number: int) -> str:
        """
        Returns n-th non empty line from `text` property.
        """
        if line_number < 1:
            raise ValueError(
                "Argument `line_number must be greater than 0.`"
            )
        lines = list(filter(
            lambda x: x if x else False, self.text.split("\n")
        ))
        if len(lines) >= line_number:
            return strip_extra_whitespace(lines[line_number - 1])
        return ""
