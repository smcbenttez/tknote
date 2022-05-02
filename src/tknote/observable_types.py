"""
Observable Types
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Protocol,
    Set,
    Type,
    TypeVar
)

from tknote.modified_list import ModifiedList

T = TypeVar('T')    # pylint: disable=invalid-name


# `@observable` class decorator
# wraps public class attributes with callback execution
def observable(attribute_names: List[str]):
    """
    Class decorator that enables specified methods to
    be observed. Registered callbacks are triggered for
    observed methods. Not intended to be called directly

    :param attribute_names: The method/property names to
        make observable
    :type attribute_names: list[str]
    """
    return lambda cls: make_observable(cls, attribute_names)


def observed_method(method):
    """
    Method decorator to wrap method execution with the
    execution of registered callbacks

    :param method: The method to decorate
    :type method: Callable
    :return: The decorated method
    :rtype: :py:func:
        `tknote.observable_types.observed_method.observable_method`
    :raises TypeError: if attempting to decorate a method already
        decorated with `observed_method`
    """
    if getattr(method, '__is_observable', False):
        raise TypeError(f"Method {method} is already observable.")

    @wraps(method)
    def observable_method(self, *args, **kwargs):
        return_value = method(self, *args, **kwargs)
        method_input: Dict[int | str, Any] = {}
        for i, arg in enumerate(args):
            method_input[i] = arg
        method_input.update(kwargs)
        self.execute_callbacks(
            method.__name__,
            method_input,
            return_value
        )
        return return_value
    observable_method.__name__ = f"observed_method({method.__name__})"
    observable_method.__is_observable = True
    return observable_method


# python properties function differently than class methods
# use property factory to wrap the original properties
# only wrap setter because we only care if the value changes
def observed_property(property_instance, property_name, docstring=None):
    """
    Property decorator to wrap the setter with callback execution

    :param property_instance: The property to decorate
    :type property_instance: property
    :param property_name: The name of the property to decorate
    :type property_name: str
    :param docstring: The property's docstring
    :type docstring: str
    """
    def getter(self):
        return property_instance.__getattribute__('fget')(self)

    def setter(self, value):
        if property_instance.__getattribute__('fset'):
            out = property_instance.__getattribute__('fset')(self, value)
            self.execute_callbacks(property_name, value, out)

    return property(getter, setter, doc=docstring)


def make_observable(cls: Type, attribute_names: List[str]):
    """
    Make a class observable using
    :py:func:`tknote.observable_types.observed_method`
    and :py:fucntion:`tknote.observed_property`

    :param cls: The class to make observable
    :type cls: type
    :param attribute_names: List of class attributes to wrap
        with callback execution
    :type attribute_names: list[str]
    """
    init = cls.__init__

    def newinit(self, *arg, **kwargs):
        init(self, *arg, **kwargs)
        self._observable_methods: Set[str] = (
            set(attribute_names)
            | getattr(self, 'observable_methods', set())
        )

    cls.__init__ = newinit
    if not attribute_names:
        # wrap all public attributes
        attribute_names = [
            x for x in dir(cls)
            if not x.startswith("_") and x not in dir(ObservableMixin)
        ]
    # wrap class attributes
    for attribute_name in attribute_names:
        if isinstance(getattr(cls, attribute_name), property):
            old_attr = getattr(cls, attribute_name)
            new_attr = observed_property(old_attr, attribute_name)
        else:
            old_attr = getattr(cls, attribute_name)
            new_attr = observed_method(old_attr)
        setattr(cls, attribute_name, new_attr)

    return cls
# end of observable_class decorator functions


class ObserverCallback(Protocol):
    """
    Protocol for a callback function

    :param data: The data from the method whose
        execution triggered the callback
    :type data: :py:class:`tknote.observable_types.CallbackData`
    """
    def __call__(self, data: CallbackData): ...


@dataclass(kw_only=True)
class CallbackData:
    """
    Dataclass to encapsulate data from the called
    method that triggered the execution of the callback

    :param caller: The object executing the callback
    :type caller: object
    :param attribute_name: The name of the method whose
        execution triggered the callback
    :type attribute_name: :py:class:`typing.Any`
    :param input_data: The input to the method whose
        execution triggered the callback
    :type input_data: :py:class:`typing.Any`
    :param output_data: The output from the method whose
        execution triggered the callback
    :type output_data: :py:class:`typing.Any`
    """
    caller: object
    attribute_name: str
    input_data: Any
    output_data: Any


class ObservableMixin:
    """
    A mixin that is intended to be used with a
    class that has been decorated with
    :py:func:`tknote.observable_types.observable`
    to provide the needed callback functionality for
    an observable type.

    Designed to be used with built in containers such as
    :py:class:`list` to allow for observers to sychronize
    behavior with specific method calls.
    """

    @property
    def observable_methods(self) -> Set[str]:
        """
        Get the set of observable methods

        :type: set[str]
        """
        return getattr(self, '_observable_methods', set())

    @property
    def callbacks(self) -> Dict[str, Set[Callable]]:
        """
        Get and set registered callbacks

        :type: dict[str, set[:py:class:`typing.Callable`]]
        """
        if not getattr(self, '_callbacks', None):
            self.callbacks = {
                x: set() for x in self.observable_methods
            }
        return self._callbacks

    @callbacks.setter
    def callbacks(
        self,
        callbacks: Dict[str, Set[Callable]]
    ):
        self._callbacks = callbacks

    def add_callback(
        self,
        attribute_name: str,
        callback: ObserverCallback,
    ):
        """
        Register callback to be executed when attribute is called
        or set

        :param attribute_name: Name of attribute to
            register with the provided callback
        :type attribute_name: str
        :param callback: The callback to register
        :type callback:
            :py:class:`tknote.observable_types.ObserverCallback`
        """
        self.callbacks[attribute_name].add(callback)

    def clear_callbacks(self):
        """
        Clear all callbacks
        """
        for method in self.observable_methods:
            self.callbacks[method] = set()

    def remove_callback(
        self,
        attribute_name,
        callback: ObserverCallback
    ):
        """
        Remove registerd callback

        :param attribute_name: The name of the attribute that
            the callback was registered to
        :type attribute_name: str
        :param callback: The callback to remove
        :type callback:
            :py:class:`tknote.observable_types.ObserverCallback`
        """
        self.callbacks[attribute_name].remove(callback)

    def execute_callbacks(self, attr_name, input_, output):
        """
        Execute all registered to an attribute

        :param attr_name: Name of attribute
        :type attr_name: str
        :param input_: The input to the method triggering callback
            execution
        :type input_: :py:class:`typing.Any`
        :param output: The output of the method triggering callback
            execution
        :type output: :py:class:`typing.Any`
        """
        for callback in self.callbacks[attr_name]:
            callback(
                CallbackData(
                    caller=self,
                    attribute_name=attr_name,
                    input_data=input_,
                    output_data=output
                )
            )


@observable(['append', 'insert', 'pop', 'reorder', 'sort'])
class ObservableList(ModifiedList, ObservableMixin, Generic[T]):
    """
    This is an extension of Python's built-in list data structure and
    is a combination of :class:`tknote.observable_types.ModifiedList`
    and :class:`tknote.observable_types.ObservableMixin` decorated with
    :py:func:`tknote.observable_types.observable`.

    See :py:class:`list` for use
    """
    ...
