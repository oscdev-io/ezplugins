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

"""EZPlugin exceptions."""

from typing import Optional


class EZPluginException(Exception):
    """Plugin-related exception."""


class EZPluginMethodNotFoundException(EZPluginException):
    """
    Exception raised when a plugin method or plugin is not found during a plugin_manager.methods() call.

    Parameters
    ----------
    method_name : Optional[str]
        Method name that was specified.

    plugin_name : Optional[str]
        Plugin name that was specified.

    Attributes
    ----------
    method_name : Optional[str]
        Method name that was specified.

    plugin_name : Optional[str]
        Plugin name that was specified.

    """

    plugin_name: Optional[str]
    method_name: Optional[str]

    def __init__(self, method_name: Optional[str], plugin_name: Optional[str]):
        """
        Exception raised when a plugin method or plugin is not found during a plugin_manager.methods() call.

        Parameters
        ----------
        method_name : Optional[str]
            Method name that was specified.

        plugin_name : Optional[str]
            Plugin name that was specified.

        """

        super().__init__("No EZPlugin method(s) found")

        self.plugin_name = plugin_name
        self.method_name = method_name
