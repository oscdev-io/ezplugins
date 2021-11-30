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

"""EZPlugins collection handling."""

import importlib
import inspect
import logging
import pkgutil
from types import ModuleType
from typing import Dict, Iterator, List, Optional, Tuple

from .exceptions import EZPluginMethodNotFoundException
from .plugin import EZPlugin, EZPluginMethod


class EZPluginModule:
    """
    Representation of a module within the plugin package hierarchy, which may contain plugins.

    Parameters
    ----------
    module_name : str
        Name of the module.

    Attributes
    ----------
    module : ModuleType
        Imported module.

    module_name : str
        Imported modules name.

    plugins : List[EZPlugin]
        List of plugins loaded from this module.

    load_exception : Optional[Exception]
        Exception if one was raised during load.

    """

    _module: Optional[ModuleType]
    _module_name: str
    _plugins: List[EZPlugin]
    _load_exception: Optional[Exception]

    def __init__(self, module_name: str):
        """
        Representation of a module within the plugin package hierarchy, which may contain plugins.

        Parameters
        ----------
        module_name : str
            Name of the module.

        Attributes
        ----------
        module : ModuleType
            Imported module.

        module_name : str
            Imported modules name.

        plugins : List[EZPlugin]
            List of plugins loaded from this module.

        load_exception : Optional[Exception]
            Exception if one was raised during load.

        """

        # Start off with the module being None and an empty plugin list
        self._module = None
        self._module_name = module_name
        self._plugins = []

        # Try import
        try:
            self._module = importlib.import_module(module_name)
        except Exception as exception:  # pylint: disable=broad-except
            # If we failed, set the status and return
            self._load_exception = exception
            return

        # Loop with class names
        for (_, plugin_class) in inspect.getmembers(self._module, inspect.isclass):

            # Only add classes that were marked as EZPlugins
            if not getattr(plugin_class, "_is_ezplugin", False):
                continue
            # Save plugin
            self._plugins.append(EZPlugin(plugin_class()))
            logging.debug("EZPlugin loaded from '%s', class '%s'", self.module_name, plugin_class)

        self._load_exception = None

    @property
    def module(self) -> Optional[ModuleType]:
        """
        Property containing the imported module.

        Returns
        -------
        Optional[ModuleType] : A module with type ModuleType that was imported (if it was imported, or None).

        """
        return self._module

    @property
    def module_name(self) -> str:
        """
        Property containing the name of the module.

        Returns
        -------
        A module str containing the module name.

        """
        return self._module_name

    @property
    def plugins(self) -> List[EZPlugin]:
        """
        Property containing a list of EZPlugin's that belong to this module.

        Returns
        -------
        A list of instantiated EZPlugin's that represent the plugin objects that were instantiated.

        """
        return self._plugins

    @property
    def load_exception(self) -> Optional[Exception]:
        """
        Property containing an exception if one was raised during load.

        Returns
        -------
        An exception raised during load if any, or None otherwise.

        """
        return self._load_exception


class EZPluginManager:
    """
    Initialize EZPluginsCollection using a list of plugin base packages.

    Plugins are mapped with the below names:
        full.module.name#ClassName
        #ClassName

    Calling a plugin by name where multiple names match will result in all plugins being called.

    Parameters
    ----------
    plugin_packages : List[str]
        Source packages to load plugins from.

    """

    _modules: List[EZPluginModule]

    def __init__(self, plugin_packages: List[str]):
        """
        Initialize EZPluginsCollection using a list of plugin base packages.

        Plugins are mapped with the below names:
            full.module.name#ClassName
            #ClassName

        Calling a plugin by name where multiple names match will result in all plugins being called.

        Parameters
        ----------
        plugin_packages : List[str]
            Source packages to load plugins from.

        """

        # Initialize the module list we loaded plugins from
        self._modules = []

        # Load plugins
        self._load_plugins(plugin_packages)

    def methods(
        self,
        where_name: Optional[str] = None,
        from_plugin: Optional[str] = None,
    ) -> Iterator[Tuple[EZPluginMethod, EZPlugin]]:
        """
        Return a generator used to iterate over plugin methods with a specific name and optionally from a specific plugin.

        Parameters
        ----------
        where_name : Optional[str]
            Limit methods returned to those matching the name provided.

        from_plugin : Optional[str]
            Limit methods returned to those belonging to a specific plugin.

        Returns
        -------
        A generator that provides tuples in the format of (EZPluginMethod, EZPlugin)

        """

        # Work out the plugins and methods we're going to call
        # Methods are unique, we'll be calling in order of method.order
        found_methods: Dict[EZPluginMethod, EZPlugin] = {}

        # Loop with our plugins matching the provided plugin_name or None
        for plugin in [x for x in self.plugins if from_plugin in [None, x.fqn, x.name, x.alias]]:
            # Loop with methods matching the method name
            for method in [x for x in plugin.methods if where_name in [None, x.name]]:
                # Check if plugin is in our call queue
                found_methods[method] = plugin

        # If we didn't find any methods, raise an exception
        if not found_methods:
            raise EZPluginMethodNotFoundException(method_name=where_name, plugin_name=from_plugin)

        # Loop with the ordered methods
        for method, plugin in sorted(found_methods.items(), key=lambda x: x[0].order):
            print(f"ITERATOR METHOD: {plugin.fqn} => {method.name} [execution order: {method.order}]")
            yield (method, plugin)

    def get_plugin(self, plugin_name: str) -> set[EZPlugin]:
        """
        Return plugin with a given name.

        This will match on the fully qualified plugin name, the class name and aliase.

        Parameters
        ----------
        plugin_name : str
            Plugin to call the method in.

        Returns
        -------
        Set of EZPlugin objects which matches the criteria.

        """

        plugin_set = set()

        # Loop with our plugins
        for plugin in self.plugins:
            # Add plugins which match the specified name
            if plugin_name in (plugin.fqn, plugin.name, plugin.alias):
                plugin_set.add(plugin)

        return plugin_set

    #
    # Internals
    #

    def _load_plugins(self, plugin_packages: List[str]) -> None:
        """
        Load plugins from the plugin_package we were provided.

        Parameters
        ----------
        plugin_packages : List[str]
            List of plugin package names to load plugins from.

        """

        # Find plugins in the plugin packages
        for plugin_package in set(plugin_packages):
            self._find_plugins(plugin_package)

    def _find_plugins(self, package_name: str) -> None:  # noqa: C901, pylint: disable=too-many-branches
        """
        Recursively search the package package_name and retrieve all plugins.

        Classes ending in "Base" are excluded.

        Parameters
        ----------
        package_name : str
            Package to load plugins from.

        """

        logging.debug("Finding plugins in '%s'", package_name)

        package = EZPluginModule(package_name)

        # Add base package module, but only if it has plugins
        if package.plugins or package.load_exception:
            self._modules.append(package)

        if not package.module:
            return

        # Grab some things we'll need below
        base_package_path = package.module.__path__  # type: ignore
        base_package_name = package.module.__name__

        # Iterate through the modules
        for _, module_name, ispkg in pkgutil.iter_modules(base_package_path, base_package_name + "."):
            # If this is a sub-package, we need to process it later
            if ispkg:
                self._find_plugins(module_name)
                continue
            # Grab plugin module
            plugin_module = EZPluginModule(module_name)
            # If we loaded OK and don't have plugins, don't add to the plugin modules list
            if not plugin_module.plugins and not plugin_module.load_exception:
                logging.debug("Ignoring plugin module '%s': No plugins", plugin_module.module_name)
                continue
            # Add to the plugin modules list
            logging.debug("Adding plugin module: %s (%s plugins)", plugin_module.module_name, len(plugin_module.plugins))
            self._modules.append(plugin_module)

    #
    # Properties
    #

    @property
    def modules(self) -> List[EZPluginModule]:
        """
        Property containing the list of modules loaded.

        Returns
        -------
        A list of modules loaded during the course of finding plugins.

        """

        return self._modules

    @property
    def plugins(self) -> List[EZPlugin]:
        """
        Return a list of plugins loaded in all modules.

        Returns
        -------
        A List[EZPlugin] of all plugins loaded.

        """

        plugins = []
        for module in self.modules:
            # Add plugins to our list
            plugins.extend(module.plugins)

        return plugins
