"""
WidgetAnimation and AnimationFrame classes
"""
from __future__ import annotations

from collections import namedtuple
from collections.abc import Generator
from typing import TYPE_CHECKING

from tknote.utils import clip_value

if TYPE_CHECKING:
    import tkinter as tk


AnimationFrame = namedtuple(
    'AnimationFrame',
    [
        # TODO: remove unneeded fields after debugging
        'widget',
        'parent_widget',
        'x',
        'y',
        'final_x',
        'final_y',
        'target_fps',
        'duration',
        'elapsed',
        'frame_number',
        'final_frame'
    ]
)


class WidgetAnimation(Generator):
    """
    Implements :py:class:`collections.abc.Generator` to generate
    animation data structured in an
    :py:class:`tknote.animation.widget_animation.AnimationFrame`
    and designed to be used with
    :py:class:`tknote.animation.animation_manager.AnimationManager`

    :param widget: The widget to animate
    :type widget: :py:class:`tkinter.Widget`
    :param parent_widget: The parent of `widget`
    :type parent_widget: :py:class:`tkinter.Widget`
    :param begin_x: Origin 'x' screen coordinate
    :type begin_x: int
    :param begin_y: Origin 'y' screen coordinate
    :type begin_y: int
    :param final_x: Destination 'x' screen coordinate
    :type final_x: int
    :param final_y: Destination 'y' screen coordinate
    :type final_y: int
    :param target_fps: The desired frames per second of the animation
    :type target_fps: int
    :param duration: The desired duration of the animation
    :type duration: int
    """
    def __init__(
        self,
        widget: tk.Widget,
        parent_widget: tk.Widget,
        begin_x: int,
        begin_y: int,
        final_x: int,
        final_y: int,
        target_fps: int,
        duration: int,       # in milliseconds
    ):
        self.widget = widget
        self.parent_widget = parent_widget
        self.begin_x = begin_x
        self.begin_y = begin_y
        self.final_x = final_x
        self.final_y = final_y
        self.target_fps = target_fps
        self.duration = duration
        # internal variables
        self._x = begin_x
        self._y = begin_y
        self._frame_number: int = 0
        self._elapsed: int = 0
        self._x_pixel_overflow: float = 0.0
        self._y_pixel_overflow: float = 0.0

    def __repr__(self) -> str:
        instance_data = {
            k: v for k, v in vars(self).items() if not k.startswith('_')
        }
        return f"<WidgetAnimation: {instance_data}>"

    @property
    def completed(self) -> bool:
        """
        Get whether or not the animation has completed

        :type: bool
        """
        return (
            self._x == self.final_x
            and self._y == self.final_y
        )

    def send(self, ignored_arg):
        """
        Implementation of :py:meth:`collections.abc.Generator.send`.
        Update the internal state of the generator

        :param ignored_arg: Just ignore it... but not in a mean way
        :raises StopIteration: if the elapsed time of the animation
            exceeds the target duration by 1000 milliseconds
        """
        if self.completed:
            raise StopIteration
        # TODO: raise exception
        # if condition triggered we have an error should probably raise
        if self._elapsed > self.duration + 1000:
            raise StopIteration
        self._x = clip_value(
            self._x + self._x_frame_delta,
            min(self.begin_x, self.final_x),
            max(self.begin_x, self.final_x)
        )
        self._y = clip_value(
            self._y + self._y_frame_delta,
            min(self.begin_y, self.final_y),
            max(self.begin_y, self.final_y)
        )

        self._frame_number += 1
        self._elapsed += self._frame_time_in_msec
        return_value = AnimationFrame(
            widget=self.widget,
            parent_widget=self.parent_widget,
            x=self._x,
            y=self._y,
            final_x=self.final_x,
            final_y=self.final_y,
            target_fps=self.target_fps,
            duration=self.duration,
            elapsed=self._elapsed,
            frame_number=self._frame_number,
            final_frame=self.completed
        )
        return return_value

    def throw(self, typ=None, val=None, tb=None):
        """
        Implementation of abstract method
        :py:meth:`collections.abc.Generator.throw`

        :raises StopIteration: if the generator has completed
        """
        raise StopIteration

    # TODO: add type annotations for properties
    @property
    def _duration_in_sec(self):
        return self.duration / 1000

    @property
    def _frame_time_in_msec(self):
        return 1000 / self.target_fps

    @property
    def _frame_time_in_sec(self):
        return 1 / self.target_fps

    @property
    def _x_dist(self):
        return self.final_x - self.begin_x

    @property
    def _y_dist(self):
        return self.final_y - self.begin_y

    @property
    def _x_float_delta(self):
        return self._x_dist / self._total_frames

    @property
    def _y_float_delta(self):
        return self._y_dist / self._total_frames

    @property
    def _x_frame_delta(self):
        pixels = int(self._x_float_delta)
        self._x_pixel_overflow += self._x_float_delta - pixels
        if self._x_pixel_overflow >= 1:
            p = int(self._x_pixel_overflow)
            self._x_pixel_overflow = self._x_pixel_overflow - p
            pixels += p
        return pixels

    @property
    def _y_frame_delta(self):
        pixels = int(self._y_float_delta)
        self._y_pixel_overflow += self._y_float_delta - pixels
        if abs(self._y_pixel_overflow) >= 1:
            p = int(self._y_pixel_overflow)
            self._y_pixel_overflow = self._y_pixel_overflow - p
            pixels += p
        return pixels

    @property
    def _total_frames(self):
        return self.duration / 1000 * self.target_fps
