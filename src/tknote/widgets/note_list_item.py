"""
NotesListItem Widget
"""
from __future__ import annotations

from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from tknote.observable_types import CallbackData
from tknote.widgets.list_item import ListItem
from tknote.widgets.resizable_label import ResizableLabel

if TYPE_CHECKING:
    from tknote.data.note_data import NoteData
    from tknote.widgets.animated_list import AnimatedList


class NoteListItem(ListItem):   # pylint: disable=too-many-ancestors
    """
    An extension of :py:class:`tknote.widgets.list_item.ListItem`
    providing ability to represent
    :py:class:`tknote.data.note_data.NoteData` in the view

    :param parent_listview: The list containing the item
    :type parent_listview:
        :py:class:`tknote.widgets.animated_list.AnimatedList`
    :param data: The note data to represent
    :type data: :py:class:`tknote.data.note_data.NoteData`
    """
    def __init__(
        self,
        parent_listview: AnimatedList,
        data: NoteData
    ) -> None:
        super().__init__(parent_listview, data)
        self.parent_listview: AnimatedList = parent_listview
        # font
        app_font = self.delegate.font
        # labels
        self.title_label = ResizableLabel(
            self,
            100,
            anchor=tk.W,
            font=app_font
        )
        self.preview_label = ResizableLabel(
            self,
            100,
            anchor=tk.W,
            font=app_font
        )
        self.date_label = tk.Label(
            self,
            anchor=tk.W,
            font=app_font,
        )
        # set label text from data
        self.update_labels()
        # separator
        self.separator = ttk.Separator(
            self,
            orient=tk.HORIZONTAL
        )
        # layout
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.title_label.grid(
            column=0,
            row=0,
            columnspan=2,
            sticky=(tk.N, tk.S, tk.E, tk.W),     # type: ignore
            pady=(6, 0)
        )
        self.preview_label.grid(
            column=1,
            row=1,
            sticky=(tk.N, tk.S, tk.E, tk.W),     # type: ignore
            pady=(0, 10)
        )
        self.date_label.grid(
            column=0,
            row=1,
            sticky=(tk.N, tk.S, tk.E, tk.W),     # type: ignore
            padx=(0, 10),
            pady=(0, 10)
        )
        self.separator.grid(
            column=0,
            row=2,
            columnspan=2,
            sticky=(tk.E, tk.W)     # type: ignore
        )
        self.update_height()

        # event bindings
        for widget in self.winfo_children():
            widget.bind(
                '<ButtonPress-1>',
                self._clicked
            )
        self.bind_all(
            '<<FontModified>>',
            self.update_height,
            add='+'
        )

        # add callback to data to keep lables in sync
        self.data.add_callback('text', self.update_labels)

    @property
    def width(self) -> int:
        """
        Get and set the widget's width

        :type: int
        """
        return self.cget('width')

    @width.setter
    def width(self, new_width: int):
        self.configure(width=new_width)
        # resize labels
        self.title_label.resize(new_width)
        self.preview_label.resize(
            new_width - self.date_label.winfo_reqwidth()
        )

    @property
    def height(self) -> int:
        """
        Get and set the widget's height

        :type: int
        """
        return self.cget('height')

    @height.setter
    def height(self, new_height):
        self.configure(height=new_height)
        self.event_generate('<<ListItemSizeModified>>')

    def set_date_text(self, *args):
        """
        Callback executed when date changes in underlying data.
        Format and set the date in the view

        :param args: Consumes unused event data
        """
        item_time = datetime.fromtimestamp(self.data.time_edited)
        now = datetime.now()
        one_day_delta = timedelta(days=1)
        seven_day_delta = timedelta(days=7)
        if now - item_time > seven_day_delta:
            self.date_label.configure(text=item_time.strftime("%x"))
        if now - item_time > one_day_delta:
            self.date_label.configure(
                text=item_time.strftime("%a %I:%M %p")
            )
        self.date_label.configure(text=item_time.strftime("%I:%M %p"))

    def update_height(self, *args):
        """
        Callback executed when the contents of the view are modified.
        Set the widget height

        :params args: Consumes unused event data
        """
        font_metrics = self.delegate.font.metrics()
        font_ascent = font_metrics['ascent']
        font_descent = font_metrics['descent']
        total_pad_y: int = 0
        title_pad_y = self.title_label.grid_info()['pady']
        if isinstance(title_pad_y, tuple):
            total_pad_y += sum(title_pad_y)
        else:
            # int
            total_pad_y = title_pad_y
        date_pad_y = self.date_label.grid_info()['pady']
        if isinstance(date_pad_y, tuple):
            total_pad_y += sum(date_pad_y)
        else:
            # int
            total_pad_y = date_pad_y
        self.height = (
            font_ascent*2
            + font_descent*2
            + total_pad_y
        )

    def update_labels(self, _: CallbackData = None):
        """
        Callback executed when underlying data is modified.
        Update labels with underlying data

        :param _: Consumes callback data
        """
        self.title_label.text = self.data.title
        self.preview_label.text = self.data.preview
        self.set_date_text()

    def _clicked(self, event: tk.Event):
        super()._clicked(event)
        self.update_height()

