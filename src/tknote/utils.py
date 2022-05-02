"""
Utility functions TkNote
"""
from __future__ import annotations

import string
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tkinter.font


def clip_value(
    val: int | float,
    min_val: int | float,
    max_val: int | float
) -> int | float:
    """
    Clip the input by provided minimum and maximum

    :param val: The value to be clipped
    :type val: int
    :param min_val: The minimum bound for the value
    :type min_val: int
    :param max_val: The maximum bound for the value
    :type: max_val: int
    :return: The clipped value
    :rtype: int or float
    :raises TypeError: if the input values are not of type `int` or `float`
    :raises ValueError: if `min_val` is greater `max_val`
    """
    if not isinstance(val, (int, float)):
        raise TypeError("argument `val` must be of type `int` or `float`")
    if not isinstance(min_val, (int, float)):
        raise TypeError(
            "argument `min_val` must be of type `int` or `float`"
        )
    if not isinstance(max_val, (int, float)):
        raise TypeError(
            "argument `max_val` must be of type `int` or `float`"
        )
    if min_val > max_val:
        raise ValueError("`min_val` must be smaller than `max_val`")
    if val <= min_val:
        return min_val
    if val >= max_val:
        return max_val
    return val


def int_to_scalar(
    val: int,
    min_val: int,
    max_val: int
) -> float:
    """
    Provides a scalar value based on the value of `val`
    within the range of `min_val` and `max_val`

    :param val: The value to convert to a scalar
    :type val: int
    :param min_val: The minimum bound of the range used to create
        the scalar
    :type min_val: int
    :param max_val: The maximum bound of the range used to create
        the scalar
    :return: A scalar based on the input values
    :rtype: float
    :raises TypeError: if the inputs are not of type `int`
    """
    if not isinstance(val, int):
        raise TypeError("argument `val` must be of type `int`")
    if not isinstance(min_val, int):
        raise TypeError("argument `min_val` must be of type `int`")
    if not isinstance(val, int):
        raise TypeError("argument `max_val` must be of type `int`")
    offset: int = min_val
    scale_range = max_val - min_val
    return (val - offset) / scale_range


def quantize_scalar(
    scalar: float,
    n_values: int
) -> float:
    """
    Quantize `scaler` value that is between 0 and 1 to a
    discrete value in the uniformly distibuted series of
    values from 0 to `n_values`.

    :param scalar: Scalar value between 0 and 1 to be quantized
    :type scalar: float
    :param n_values: Number of discrete values to be used for
        quantization
    :type n_values: int
    :return: The quantized value
    :rtype: float
    :raises TypeErorr: if `scalar` is not a `float` or `n_values` is
        not an `int`
    """
    if not isinstance(scalar, float):
        raise TypeError("`scalar` must be of type `float`")
    if not isinstance(n_values, int):
        raise TypeError("`n_values` must be of type `int`")
    step_size: float = 1 / (n_values - 1)
    series_index = int((scalar + (step_size / 2)) * (n_values - 1))
    return (
        series_index
        * step_size
    )


def scalar_to_int(
    scalar: float,
    min_val: int,
    max_val: int
) -> int:
    """
    Map a `scalar` value between 0 and 1
    to a range expressed by `min_val` and `max_val`

    :param scalar: The scalar to convert to an integer
    :type scalar: float
    :param min_val: The minimum bound of the scale
    :type min_val: int
    :param max_val: The maximum bound of the scale
    :type max_val: int
    :return: The scaled integer value
    :rtype: int
    :raises TypeError: if `scalar` is not of type `float`
    :raises TypeError: if `min_val` or `max_val` is not of type `int`
    """
    if not isinstance(scalar, float):
        raise TypeError("`scalar` must be of type `float`")
    if not isinstance(min_val, int):
        raise TypeError("`min_val` must be of type `int`")
    if not isinstance(max_val, int):
        raise TypeError("`max_val` must be of type `int`")
    offset: int = min_val
    value_range: int = max_val - min_val
    mapped_value = scalar * value_range
    return int(mapped_value) + offset


def strip_tailing_whitespace(input_str: str) -> str:
    """
    Strip all tailing whitespace from a string

    :param input_str: The string to be stripped
    :type input_str: str
    :return: The stripped string
    :rtype: str
    :raises TypeError: if `input_str` is not of type `str`
    """
    if not isinstance(input_str, str):
        raise TypeError("`input_str` must be of type `str`")
    if not input_str:
        return input_str
    i = len(input_str) - 1
    while i > 0:
        if input_str[i] in string.whitespace:
            i -= 1
        else:
            break
    return input_str[:i + 1]


def strip_leading_whitespace(input_str: str) -> str:
    """
    Strip all leading whitespace from a string

    :param input_str: The string to be stripped
    :type input_str: str
    :return: The stripped string
    :rtype: str
    :raises TypeError: if `input_str` is not of type `str`
    """
    if not isinstance(input_str, str):
        raise TypeError("`input_str` must be of type `str`")
    if not input_str:
        return input_str
    i = 0
    while i < len(input_str):
        if input_str[i] in string.whitespace:
            i += 1
        else:
            break
    return input_str[i:]


def strip_extra_whitespace(input_str: str) -> str:
    """
    Strips all leading and tailing whitespace

    :param input_str: The string to be stripped
    :type input_str: str
    :return: The stripped string
    :rtype: str
    :raises TypeError: if `input_str` is not of type `str`
    """
    return strip_leading_whitespace(strip_tailing_whitespace(input_str))


def truncate_str(input_str: str,
                 font: tkinter.font.Font,
                 avg_chr_size: int,
                 max_size: int) -> str:
    """
    Truncates a string if it exceeds the specified maximum display width

    :param input_str: The string to be truncated
    :type input_str: str
    :param font: The tkinter font used to display the string
    :type font: :class:`tkinter.font.Font`
    :param avg_char_size: The average pixel width of a character
        displayed using the specified font
    :type avg_char_size: int
    :param max_size: The maximum width to be displayed
    :return: The truncated string
    :rtype: str
    """
    truncated: bool = False
    # this is an overestimate, but it does improve performance 10x
    max_len_estimate = int(
        (max_size - (avg_chr_size * 3)) // avg_chr_size
    )
    if len(input_str) >= max_len_estimate:
        output_str = input_str[:max_len_estimate]
    else:
        output_str = input_str
    while (
        output_str
        and (font.measure(output_str) + (avg_chr_size * 3)) >= max_size
    ):
        truncated = True
        output_str = output_str[:-1]
    if not truncated:
        return output_str
    return output_str + "..."
