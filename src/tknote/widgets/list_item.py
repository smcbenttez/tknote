"""
ListViewItem widget
"""
from __future__ import annotations

from abc import abstractmethod
import tkinter as tk
from typing import Any, TYPE_CHECKING

from tknote.widgets.widget_delegate import WidgetDelegate

if TYPE_CHECKING:
    from tknote.widgets.animated_list import AnimatedList


class ListItem(tk.Frame):  # pylint: disable=too-many-ancestors
    """
    A :py:mod:`tkinter` widget to be used with
    :py:class:`tknote.widgets.animated_list.AnimatedList`.
    It is an extension of :py:class:`tkinter.Frame`

    :param parent_listview: The list that will contain the item
    :type parent_listview:
        :py:class:`tknote.widgets.animated_list.AnimatedList`
    """
    def __init__(
            self,
            parent_listview: AnimatedList,
            data: Any
    ):
        super().__init__(
            parent_listview.scrollview,
            class_='ListItem'
        )
        # do not use size of contents to set size for entire item
        self.grid_propagate(False)
        # attributes
        self._is_selected: bool = False
        self.data = data
        self.delegate: ListItemDelegate = parent_listview
        # TODO deal with colors in a platform agnostic way
        self.og_color: str = self['background']
        # NOTE this will only work on macOS
        self.selection_color: str = 'systemWindowBackgroundColor4'

        # bind to mouse click
        self.bind(
            '<ButtonPress-1>',
            self._clicked
        )

    @property
    def is_selected(self) -> bool:
        """
        Get whether or not the widget is selected

        :type: bool
        """
        return self._is_selected

    @property
    def height(self) -> int:
        """
        Get and set the widget's height

        :type: int
        """
        return self.cget('height')

    @height.setter
    def height(self, new_height: int):
        self.configure(height=new_height)

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

    def select(self):
        """
        Select the widget
        """
        if self.is_selected:
            return
        self.configure(background=self.selection_color)
        for child in self.winfo_children():
            if 'background' in child.configure().keys():
                child.configure(background=self.selection_color)
        self._is_selected = True

    def deselect(self):
        """
        Deselect the widget
        """
        if not self.is_selected:
            return
        self.configure(background=self.og_color)
        for child in self.winfo_children():
            if 'background' in child.configure().keys():
                child.configure(background=self.og_color)
        self._is_selected = False

    def _clicked(self, _) -> None:
        self.delegate.list_item_clicked(self)


class ListItemDelegate(WidgetDelegate):
    """
    Abstract class extending :py:class:`tknote.widgets.WidgetDelegate`
    defining required delegate methods for
    :py:class:`tknote.widgets.list_item.ListItem`
    """
    @abstractmethod
    def list_item_clicked(self, list_item: ListItem):
        """
        Called when the `ListItem` is clicked

        :abstractmethod:
        :param list_item: The `ListItem` that was clicked
        :type list_item: :py:class:`tknote.widgets.list_item.ListItem`
        """
        ...
