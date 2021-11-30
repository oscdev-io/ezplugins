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

"""EZPlugins tests."""

from typing import Dict

import ezplugins

from ..base import BaseTest


class TestPackageNoExist(BaseTest):
    """Test for the case that the plugin package doesn't exist."""

    data: Dict[str, ezplugins.EZPluginManager] = {}

    def test_plugin_load(self) -> None:
        """Test loading of plugins."""
        self.data["plugins"] = ezplugins.EZPluginManager([self.plugin_path("some_package_does_not_exist")])

        expected_modules = [
            (
                "tests.t20_exceptions.some_package_does_not_exist",
                ModuleNotFoundError,
                "ModuleNotFoundError(\"No module named 'tests.t20_exceptions.some_package_does_not_exist'\")",
            )
        ]

        received_modules = [(x.module_name, type(x.load_exception), repr(x.load_exception)) for x in self.data["plugins"].modules]

        assert received_modules == expected_modules, "Result from plugin load does not match"
