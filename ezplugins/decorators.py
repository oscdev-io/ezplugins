#
# SPDX-License-Identifier: MIT
#
# Copyright (C) 2019-2021, AllWorldIT.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""EZPlugin decorators."""

from typing import Callable, Optional, Type, TypeVar

EZPT = TypeVar("EZPT")


def ezplugin(cls: Type[EZPT]) -> Type[EZPT]:
    """Decorate a class as being a loadable EZPlugin."""

    def decorator(cls: Type[EZPT]) -> Type[EZPT]:
        # Set class attribute
        setattr(cls, "_is_ezplugin", True)
        return cls

    return decorator(cls)


def ezplugin_metadata(*, alias: Optional[str] = None) -> Callable[[EZPT], EZPT]:
    """
    Decorate a class as being a loadable plugin, with metadata.

    Parameters
    ----------
    alias : Optioanl[str]
        Plugin class alias, used when specifying a specific plugin to call. This makes it easier to specify a plugin name
        instead of using the full plugin module name.

    """

    def decorator(cls: EZPT) -> EZPT:
        # Set function attribute
        setattr(cls, "_is_ezplugin", True)
        # Setup metadata if it exists
        if alias:
            setattr(cls, "_ezplugin_alias", alias)
        return cls

    return decorator


def ezplugin_method(*, order: int = 5000) -> Callable[[EZPT], EZPT]:
    """
    Decorate a function as an EZPlugin method and to provide it with an optional run order.

    This will allow the plugin to be called by the EZPlugin framework.

    Parameters
    ----------
    order : int
        Run order of method if multiple methods are being executed. Defaults to 5000. Methods are executed lowest to highest.

    """

    def decorator(func: EZPT) -> EZPT:
        # Set function attribute
        setattr(func, "_ezplugin_order", order)
        return func

    return decorator
