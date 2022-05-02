"""
AppStateData Class
"""
from __future__ import annotations

import ast
from dataclasses import asdict, astuple, dataclass
import json
from typing import Any, Tuple


@dataclass(repr=False, kw_only=True)
class AppStateData:
    id_: int | None
    window_width: int
    window_height: int
    window_x_offset: int
    window_y_offset: int
    _window_split_position: str
    list_index_selected: int
    list_sort_key: str
    list_sort_ascending: int
    app_font: str
    app_font_size: int

    def __repr__(self):
        return str(asdict(self))

    # @classmethod
    # def from_json(cls, json_str):
    #     return cls.from_dict(json.loads(json_str))

    @property
    def db_id(self) -> int | None:
        return self.id_

    @db_id.setter
    def db_id(self, db_id: int) -> None:
        self.id_ = db_id

    @property
    def window_geometry(self) -> str:
        return (
            f"{self.window_width}x{self.window_height}"
            + f"+{self.window_x_offset}+{self.window_y_offset}"
        )

    @window_geometry.setter
    def window_geometry(self, tk_geometry_str: str) -> None:
        win_geo = tuple(
            int(x) for x in tk_geometry_str.replace("x", "+").split("+")
        )
        self.window_width, self.window_height = win_geo[:2]
        self.window_x_off, self.window_y_off = win_geo[2:]

    @property
    def window_split_position(self) -> Tuple:
        position = ast.literal_eval(self._window_split_position)
        if isinstance(position, tuple):
            return position
        raise TypeError(
            "AppState could not parse a tuple from data "
            + f"for _window_split_position: {self._window_split_position}"
        )

    @window_split_position.setter
    def window_split_position(
        self,
        screen_coord: Tuple[int, int]
    ) -> None:
        self._window_split_position = str(screen_coord)

    @property
    def json(self):
        return json.dumps(asdict(self))

    @property
    def as_tuple(self) -> Tuple[Any, ...]:
        return astuple(self)
