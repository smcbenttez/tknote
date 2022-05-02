"""
ResizableLabel Widget
"""
from __future__ import annotations

import tkinter as tk
from tkinter import font as tk_font

from tknote.utils import truncate_str


class ResizableLabel(tk.Label):  # pylint: disable=too-many-ancestors
    """
    An extension of :py:class:`tkinter.Label` that displays
    only the amount of text possible with the configured width
    of the label as well as displaying a visual indication
    that there is underlying text data that is not displayed
    with an ellipsis

    :param parent: The parent widget
    :type parent: :py:class:`tkinter.Widget`
    :param pixel_width: The desired width (in pixels) of the label
    :type pixel_width: int
    :param kwargs: Keyword arguments
    """
    def __init__(self, parent, pixel_width: int, **kwargs):
        super().__init__(parent, **kwargs)
        # _text is the entire string before being truncated
        self._text: str = ""
        self._displayed_text: tk.StringVar = tk.StringVar()
        self.configure(textvariable=self._displayed_text)
        self.pixel_width = tk.IntVar()
        self.pixel_width.set(pixel_width)
        self.pixel_width.trace_add(
            mode='write',
            callback=self.update_displayed_text
        )

    @property
    def font(self) -> tk_font.Font:
        """
        Get and set widget's font

        :type: :py:class:`tkinter.font.Font`
        """
        return tk_font.nametofont(self.cget('font'))

    @font.setter
    def font(self, font: tk_font.Font):
        self.configure(font=font)

    @property
    def font_avg_chr_size(self) -> int:
        """
        Get the average character size in pixel for the widget's font

        :type: int
        """
        return (
            self.font.measure(
                "".join([chr(i) for i in range(128)])
            ) // 128
        )

    @property
    def text(self) -> str:
        """
        Get and set the label's full text

        :type: str
        """
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self.update_displayed_text()

    @property
    def displayed_text(self) -> str:
        """
        Get and set the text that widget is displaying

        :type: str
        """
        return self._displayed_text.get()

    @displayed_text.setter
    def displayed_text(self, text: str):
        self._displayed_text.set(text)

    @property
    def text_var(self) -> tk.Variable | None:
        """
        Get and set the variable used by the widget to share it's value

        :type: :py:class:`tkinter.Variable`
        """
        var = getattr(self, '_text_var', None)
        if var:
            return var
        return None

    @text_var.setter
    def text_var(self, text_var: tk.Variable):
        self._text_var = text_var
        self._text_var.trace_add(
            mode='write',
            callback=self._var_callback
        )

    def resize(self, new_width: int) -> None:
        """
        Resize the label's width

        :param new_width: The value to set the widget's width to
        :type new_width: int
        """
        self.pixel_width.set(new_width)

    def update_displayed_text(self, *args):
        """
        Update the label's displayed text according to it's width

        :param args: Consumes the callback data
        """
        truncated_text = truncate_str(
            input_str=self.text,
            font=self.font,
            avg_chr_size=self.font_avg_chr_size,
            max_size=self.pixel_width.get() - 10
        )
        self.displayed_text = truncated_text

    def _var_callback(self, *args) -> None:
        if self.text_var:
            self.text = self.text_var.get()
        self.update_displayed_text()

