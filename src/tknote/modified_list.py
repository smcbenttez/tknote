"""
Modifed verion of Python's :py:class:`list`
"""
from __future__ import annotations

from typing import Generic, Iterable, TypeVar

T = TypeVar('T')


class ModifiedList(list):
    """
    Extenstion of Python's built-in list data structure.
    See :py:class:`list` for use
    """

    def reorder(self, new_order: Iterable[int]):
        """
        Reorder the list's items according to the provided
        order. Designed to take the output of the `ModifiedList`
        sort function

        :param new_order: The desired order of the list's items
            as an iterable of integers representing the indecies
            of the items' current positions.
        :type new_order: :py:class:`typing.Iterable`[int]
        """
        if not new_order:
            return
        new_positions, _ = zip(*sorted(
            enumerate(new_order),
            key=lambda x: x[1]
        ))
        if not self:
            return
        enumerated_reordered_list = sorted(
            zip(new_positions, self),
            key=lambda x: x[0]
        )
        _, reordered_list = zip(*enumerated_reordered_list)
        super().clear()
        super().extend(reordered_list)

    def sort(self, key=lambda x: x, reverse=False):
        """
        Sort the items of the list in place.

        :param key: Specifies a function of one argument
            that is used to extract a comparison key from
            each element in iterable
        :type key: :py:class:`typing.Callable`
        :param reverse: Whether or not to reverse the sort order
        :type reverse: bool
        :return: The sort order of the list items
        :rtype: tuple[int, ...]
        """
        if not self:
            return tuple()
        sorted_enumerated_list = sorted(
            enumerate(self),
            key=lambda x: key(x[1]),
            reverse=reverse
        )
        sort_order, sorted_list = zip(*sorted_enumerated_list)
        super().clear()
        super().extend(sorted_list)
        return sort_order
