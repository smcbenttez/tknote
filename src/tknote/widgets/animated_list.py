"""
AnimatedList Widget and ListDelegate Class
"""
from __future__ import annotations

from abc import abstractmethod
import tkinter as tk
from typing import List, Tuple, TYPE_CHECKING

from tknote.animation.widget_animation import WidgetAnimation
from tknote.observable_types import ObservableList
from tknote.widgets.list_item import ListItem, ListItemDelegate
from tknote.widgets.scrollable_frame import ScrollableFrame
from tknote.widgets.widget_delegate import WidgetDelegate
from tknote.tk_geometry import TkGeometry

if TYPE_CHECKING:
    from tkinter import font as tk_font
    from tknote.animation.animation_manager import AnimationManager
    from tknote.observable_types import CallbackData


class AnimatedList(ScrollableFrame, ListItemDelegate):
    """
    An animated list widget for `tkniter`. It is an extension and
    combination of
    :py:class:`tknote.widgets.scrollable_frame.ScrollableFrame`
    and :py:class:`tknote.widgets.animated_list.ListDelegate`

    :param animation_manager: The animation manager for the widget
    :type animation_manager:
        :py:class:`tknote.animation.animation_manager.AnimationManager`
    :param delegate: The delegate for the widget
    :type delegate: :py:class:`tknote.widgets.animated_list.ListDelegate`
    """
    def __init__(
        self,
        /,
        animation_manager: AnimationManager | None,
        delegate: ListDelegate,
        *args
    ):
        super().__init__(*args, class_='AnimatedFrame')

        # delegate
        self.delegate = delegate
        # animation manager
        self.animation_manager: AnimationManager | None = (
            animation_manager
        )
        if self.animation_manager:
            self.animation_manager.add_callback(
                self.update_scrollview_size
            )
        # properties
        self._visible_items_slice: slice = slice(0)
        self.items: ObservableList[ListItem] = ObservableList()
        # TODO configure this in a more intuitive way
        self.gui_updated_callback = self.update_visible_items
        # event bindings
        self.bind_class(
            'ListItem',
            '<<ListItemSizeModified>>',
            self._item_size_modified
        )
        # setup callbacks
        self._configure_callbacks()

    # ListItemDelegate methods
    @property
    def font(self) -> tk_font.Font:
        """
        Get the application font

        :type: :py:class:`tkinter.font.Font`
        """
        return self.delegate.font

    def list_item_clicked(self, list_item: ListItem):
        """
        Delegate method executed when an instance of
        :py:class:`tknote.widgets.list_item.ListItem` is clicked.
        :py:meth:
        `tknote.widgets.animated_list.ListDelegate.list_index_selected`
        is called

        :param list_item: The `ListItem` that was clicked
        :type list_item: :class:`tknote.widgets.list_item.ListItem`
        """
        self.delegate.list_index_selected(
            self.items.index(list_item)
        )

    @property
    def delegate(self) -> ListDelegate:
        """
        Get or set the `AnimatedList`'s delegate

        :type: :py:class:`tknote.widgets.animated_list.ListDelegate`
        """
        return self._delegate

    @delegate.setter
    def delegate(self, delegate: ListDelegate):
        """
        Set `delegate`
        """
        self._delegate = delegate

    @property
    def visible_items(self) -> List[ListItem]:
        """
        Get list of currently visible list items

        :return: :py:class:`tknote.widgets.list_item.ListItem`
        """
        return self.items[self._visible_items_slice]

    @property
    def visible_width(self) -> int:
        """
        Get the number of pixels displayed by the `AnimatedList`

        :type: int
        """
        return (
            TkGeometry.from_str(self.winfo_geometry()).width
            - TkGeometry.from_str(self.scrollbar.winfo_geometry()).width
        )

    def scroll_to_item(self, item: ListItem):
        """
        Scroll to the specified item

        :param item: The `ListItem` to scroll to
        :type item: :py:class:`tknote.widgets.list_item.ListItem`
        """
        scrollview_span = self.scrollbar.get()
        item_pos = TkGeometry.from_str(item.winfo_geometry())
        scrollview_height = self.scrollview.winfo_height()
        item_top_norm = item_pos.y_off / scrollview_height
        item_bottom_norm = (
            (item_pos.y_off + item_pos.height) / scrollview_height
        )
        if item_top_norm < scrollview_span[0]:
            self.canvas.yview('moveto', item_top_norm)
        elif item_bottom_norm > scrollview_span[1]:
            self.canvas.yview('moveto', item_bottom_norm)

    def update_scrollview_size(self):
        """
        Resizes the scrollview according to items containted
        in the list.
        """
        total_item_height = sum([item.height for item in self.items])
        self.scrollview.configure(
            width=4096,
            height=total_item_height
        )

    def update_visible_items(self):
        """
        Updates
        :py:attr:`tknote.widget.animated_list.AnimatedList.visible_items`
        """
        visible_portion = self.scrollbar.get()
        visible_pixels = self._get_visible_pixels(visible_portion)
        visible_items = [
            x for x in enumerate(self.items)
            if self._is_item_visible(x[1], visible_pixels)
        ]
        if not visible_items:
            return
        visible_indecies, _ = zip(*visible_items)
        self._visible_items_slice = slice(
            visible_indecies[0], visible_indecies[-1] + 1
        )
        for item in self.items[self._visible_items_slice]:
            item.width = self.visible_width
        self.update_scrollview_size()

    def _configure_callbacks(self):
        # internal callbacks for keeping UI in sync
        self.items.add_callback('append', self._item_appended)
        self.items.add_callback('insert', self._item_inserted)
        self.items.add_callback('pop', self._item_popped)
        self.items.add_callback('sort', self._items_sorted)
        self.items.add_callback('reorder', self._items_reordered)
        # callbacks for changes to data in model
        self.delegate.list_data.add_callback(
            'pop',
            lambda x: (
                self.items.pop(x.input_data[0]) if x.input_data
                else self.items.pop()
            )
        )
        self.delegate.list_data.add_callback(
            'sort',
            lambda x: (
                self.items.reorder(x.output_data)
            )
        )

    def _get_index_pixel_start(self, index: int) -> int:
        y_running_sum: int = 0
        for item in self.items[:index]:
            y_running_sum += item.height
        return y_running_sum

    def _get_visible_pixels(
        self,
        visible_portion: Tuple[float, float]
    ) -> Tuple[int, int]:
        """
        Return the visible span of the list view in pixels.
        """
        scrollview_height = self.scrollview.winfo_height()
        return (
            int(visible_portion[0]*scrollview_height),
            int(visible_portion[1]*scrollview_height)
        )

    def _is_item_visible(
        self,
        widget: tk.Widget,
        visible_pixels: Tuple[int, int]
    ) -> bool:
        """
        Checks whether or not the specified item is visible
        on screen. Returns `True` if item is visible.
        """
        # TODO: make this dynamic based on item heights
        item_geometry = TkGeometry.from_str(widget.winfo_geometry())
        half_default_item_height = 64 // 2
        item_y_off = item_geometry.y_off
        return (
            (visible_pixels[0]-half_default_item_height)
            < item_y_off
            < (visible_pixels[1]+half_default_item_height)
        )

    def _item_appended(self, data: CallbackData):
        item = data.input_data[0]
        self._place_item(
            index=len(self.items) - 1,
            item=item
        )

    def _item_inserted(self, data: CallbackData):
        index = data.input_data[0]
        item = data.input_data[1]
        self._place_item(index=index, item=item)
        self._shift_items_down(start_index=index + 1)

    def _item_size_modified(self, event: tk.Event):
        self._update_item_positions(
            tuple(range(len(self.items))),
            animate=False
        )
        self.update_scrollview_size()

    def _item_popped(self, data: CallbackData):
        if data.input_data:
            index = data.input_data[0]
        else:
            index = None
        popped_item = data.output_data
        if index is not None:
            self._shift_items_up(index)
        # remove item from view
        popped_item.place_forget()
        # destroy widget and its children
        for widget in popped_item.winfo_children():
            widget.destroy()
        popped_item.destroy()

    def _items_reordered(self, data: CallbackData):
        self._reorder_items()

    def _items_sorted(self, data: CallbackData):
        self._reorder_items()

    def _move_items(
        self,
        item_indecies: Tuple[int, ...]
    ):
        """
        Move widgets using the place method.
        """
        y_running_sum = self._get_index_pixel_start(min(item_indecies))
        for i in item_indecies:
            # move the widgets without animation
            item = self.items[i]
            item.place(
                in_=self.scrollview,
                x=0,
                y=y_running_sum,
                anchor='nw',
                bordermode='inside'
                )
            y_running_sum += item.height

    def _move_items_animated(
        self,
        item_indecies: Tuple[int, ...]
    ):
        """
        Move items using animation via the AnimationManager.
        """
        if not self.animation_manager:
            raise NotImplementedError(
                """An instance of AnimationManager is needed
                in order to call `move_list_items_animated`"""
            )
        animations: List[WidgetAnimation] = []
        # create an animation for the scroll view resizing
        # TODO: add ability to animate widget resizing...
        # use running sum to account for different sized items
        y_running_sum = self._get_index_pixel_start(min(item_indecies))
        for i in item_indecies:
            # create widget animations for each widget that needs to move
            item = self.items[i]
            if i == 0:
                item.tkraise()
            animations.append(
                WidgetAnimation(
                    widget=item,
                    parent_widget=self.scrollview,
                    begin_x=item.winfo_x(),
                    begin_y=item.winfo_y(),
                    final_x=0,
                    final_y=y_running_sum,
                    target_fps=60,
                    duration=250
                )
            )
            y_running_sum += item.height
        # give those widget animations to the animation manager
        self.animation_manager.schedule_animations(animations)

    def _place_item(self, index: int, item: ListItem):
        # TODO: add animation for new item, just place for now
        item.lower()
        item.width = self.visible_width
        item.place(
            in_=self.scrollview,
            x=0,
            y=self._get_index_pixel_start(index),
            anchor=tk.NW,
            bordermode=tk.INSIDE
        )
        self.update_scrollview_size()

    def _reorder_items(self):
        """
        Reorders items in view according to the provided indecies.
        """
        self._update_item_positions(tuple(range(len(self.items))))

    def _shift_items_down(self, start_index: int):
        item_indecies = tuple(
            i for i in range(start_index, len(self.items))
        )
        self._update_item_positions(item_indecies)

    def _shift_items_up(self, index: int):
        item_indecies = tuple(
            i for i in range(index, len(self.items))
        )
        self._update_item_positions(item_indecies)

    def _update_item_positions(
        self,
        item_indecies: Tuple[int, ...],
        animate: bool = True
    ):
        """
        Udate the UI using animation if an animation manager is available.
        Otherwise update the UI without animation.
        """
        if not item_indecies:
            return
        if animate and self.animation_manager:
            self._move_items_animated(item_indecies)
        else:
            self._move_items(item_indecies)


class ListDelegate(WidgetDelegate):
    """
    Abstract class that extends
    :py:class:`tknote.widgets.WidgetDelegate` that defines
    the necessary delegate methods for
    :py:class:`tknote.widgets.animated_list.AnimatedList`
    """

    @property
    @abstractmethod
    def list_data(self) -> ObservableList:
        """
        Get backing data for list

        :abstractmethod:
        :type: :py:class:`tknote.observable_types.ObservableList`
        """
        ...

    @abstractmethod
    def list_index_selected(self, index_selected: int):
        """
        Delegate method called when an item in the list is selected

        :abstractmethod:
        :param index_selected: The list index of the item selected
        :type index_selected: int
        """
        ...
