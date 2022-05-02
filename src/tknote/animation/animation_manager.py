"""
AnimationManager Class
"""
from __future__ import annotations

from collections import deque
import tkinter as tk
from typing import Callable, Deque, Iterable, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from tknote.animation.widget_animation import (
        AnimationFrame,
        WidgetAnimation
    )


class AnimationManager:
    """
    Provides rudimentary animation support for :py:mod:`tkinter`
    by using :py:meth:`tkinter.Misc.after` to incrementally
    move widgets using :py:meth:`tkinter.Place.place_configure`
    provided with data from :py:class:`tknote.animation.WidgetAnimation`

    :param app_root: The root application :py:mod:`tkinter` object
    :type app_root: :py:class:`tkinter.Tk`
    """
    def __init__(self, app_root: tk.Tk):
        self.app: tk.Tk = app_root
        # a tick rate half the frame interval to reach
        # the target seems to work well.
        self.tick_rate: int = 8
        self.after_id: int | None = None
        self.scheduled_animations: Deque[WidgetAnimation] = deque()
        self.running_animations: Deque[WidgetAnimation] = deque()
        self._animation_in_progress = False
        self._callbacks: Set[Callable] = set()
        self._run()

    def add_callback(self, callback: Callable):
        """
        Register callback to be executed when all animations finish

        :param callback: The callback fucntion
        :type: :py:class:`typing.Callable`
        """
        self._callbacks.add(callback)

    def schedule_animations(self, animations: Iterable[WidgetAnimation]):
        """
        Schedule new animations to be run.

        :param animations: Animations to be scheduled to run
        :type animations: :py:class:`typing.Iterable`[
                :py:class:
                    `tknote.animation.widget_animation.WidgetAnimation`
            ]
        """
        self.scheduled_animations.extend(animations)

    def _execute_callbacks(self):
        for callback in self._callbacks:
            callback()

    def _run(self):
        """
        Run all added animations. Should not explicitly be called.
        """
        if not self.scheduled_animations:
            if self._animation_in_progress:
                self._animation_in_progress = False
                self._execute_callbacks()
            # always running and waiting for animations
            self.after_id = self.app.after(self.tick_rate, self._run)
        else:
            self._animation_in_progress = True
            frames: Deque[AnimationFrame] = deque()
            while self.scheduled_animations:
                animation = self.scheduled_animations.popleft()
                try:
                    # StopIteration raised when animation finishes.
                    frames.append(next(animation))
                    self.running_animations.append(animation)
                except StopIteration:
                    # Do not requeue finished animations.
                    continue
            while self.running_animations:
                self.scheduled_animations.appendleft(
                    self.running_animations.pop()
                )
            while frames:
                frame = frames.popleft()
                try:
                    frame.widget.place(
                        in_=frame.parent_widget,
                        x=frame.x,
                        y=frame.y,
                        anchor='nw',
                        bordermode='inside'
                    )
                except tk.TclError:
                    # Will happen when placing a deleted widget
                    # Occurs when spamming Delete button
                    continue
            self.after_id = self.app.after(self.tick_rate, self._run)
