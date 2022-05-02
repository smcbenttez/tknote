"""
QuantizedScale Widget
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from tknote.utils import quantize_scalar


class QuantizedScale(ttk.Scale):  # pylint: disable=too-many-ancestors
    """
    An extension of :py:class:`tkinter.ttk.Scale` that quantizes
    the output of the widget to uniformly distributed discrete
    values defined by the keyword argument `steps`

    :param args: Positional arguments
    :param kwargs: Keyword arguments
    """
    def __init__(self, *args, **kwargs):
        # variable used to capture the raw input
        self._raw_input_var: tk.DoubleVar = tk.DoubleVar()
        self._raw_input_var.trace_add('write', self.input_modified)

        self._quantized_input_var: tk.DoubleVar
        self.steps: int
        if 'steps' in kwargs:
            self.steps = kwargs['steps']
            # remove the kwarg before passing it to super().__init__
            del kwargs['steps']
        else:
            self.steps = 5
        if 'variable' in kwargs:
            # intercept the variable passed to the constructor
            # variable used for sharing quantized input
            self._quantized_input_var: tk.DoubleVariable = (
                kwargs['variable']
            )
        # pass the internally created variable to super().__init__
        # variable used for getting raw input value
        kwargs['variable'] = self._raw_input_var
        super().__init__(*args, **kwargs)

    @property
    def value(self) -> float:
        """
        Get and set the value displayed by the widget

        :type: float
        """
        return self.cget('value')

    @value.setter
    def value(self, value: float):
        quantized_value = quantize_scalar(value, self.steps)
        if self._quantized_input_var:
            self._quantized_input_var.set(quantized_value)
        else:
            self.configure(value=quantized_value)

    @property
    def var(self) -> tk.DoubleVar | None:
        """
        Get and set the variable used to share the widget's value

        :type: :py:class:`tkinter.DoubleVar` or None
        """
        return getattr(self, '_quantized_input_var', None)

    @var.setter
    def var(self, var: tk.DoubleVar):
        self._quantized_input_var = var

    def configure(self, cnf=None, **kwargs):
        """
        Configure the widget with specified kwargs

        :param cnf: Undocumented argument used by
            :py:method:`tkinter.Misc._configure`
        :param kwargs: Keyword arguments
        """
        if 'variable' in kwargs:
            self._quantized_input_var = kwargs['variable']
            del kwargs['variable']
            # kwargs['variable'] = self._raw_input_var
        super().configure(cnf, **kwargs)

    def input_modified(self, *args):
        """
        Callback executed when the widget's input is modified
        Set the value of the widget

        :param args: Consumes the callback data
        """
        self.value = self._raw_input_var.get()
