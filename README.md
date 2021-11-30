# EZPlugins

EZPlugins is an easy to use plugin API.

# Quick Start

Defining a basic plugin can be done using the following in `mypackage/plugins/myplugin.py`
```python
import ezplugins

@ezplugins.ezplugin
class MyPlugin:

    # Plugin objects are initialized on load
    def __init__(self):
        print("Plugin INIT")

    # Methods must be decorated so they can be run
    @ezplugins.ezplugin_method()
    def some_method(self, param1, param2):
        return f"{param1=}, {param2=}"
```

Loading the plugin and running the method can be done using...
```python
import ezplugins

# Load plugins from mypackage.plugins
plugin_manager = ezplugins.EZPluginManager(["mypackage.plugins"])

# Call the method some_func in each plugin
for method, _ in plugin_manager.methods(with_name="some_func"):
    result = method.run("param1", "param2")
    print(f"RESULT: {result}")
```

Yes, there is a `_` in the above, this is actually the plugin the method is from. In this case we don't need it.

# Defining Plugins

Taking the quickstart example, plugins are defined by decorating them with `@ezplugins.ezplugin`. The result of this would be the class is marked as being an EZPlugins class that is instantiated during plugin load.
```python
import ezplugins

@ezplugins.ezplugin
class MyPlugin:
    ...
```

Plugins are instantiated during load. Plugin methods are called using this instantiated object.

Multiple plugin classes can be defined in the same file. Sub-modules are transversed.

The only restriction relating to plugins is that the plugin package must be a valid Python package.

Internal plugin names are set to the path of the module it is loaded from within the `PYTHONPATH` and suffixed with `#ClassName` , in this case it would be `package.path#MyPlugin`. This can be used to call a specific plugin. On a side note, to make things easier, plugins can also be called using `#ClassName`, keep in mind though that one can have two classes with the same name in different modules.

See [Calling Plugins](#calling-plugins) for more info on using plugin names.

## Plugin Aliases

Plugin aliases can be provided using the `@ezplugins.ezplugin_metadata` decorator...

```python
import ezplugins

@ezplugins.ezplugin_metadata(alias="CoolPlugins")
class MyPlugin:
    ...
```

A plugin alias can be provided, which may better suite the needs of application. The alias can be anything, it may also match another fully qualified plugin name, or class name. This plugin alias is looked up when a call to a specific plugin is made (see [Calling Plugins](#calling-plugins) for more info).

This poses an interesting scenario of being able to run a plugin method before another plugin method if the ordering is changed (see [Method Ordering](#method-ordering)).

# Defining Plugin Methods

Plugin methods must be decorated, this allows EZPlugins to know that this method can be called. The decorator used for methods are `@ezplugins.ezplugin_method()`. The result of using this decorator is the method will get additional attributes set which EZPlugins looks for when determining which methods can be run or not.

```python
import ezplugins

@ezplugins.ezplugin
class MyPlugin:

    ...

    # Methods must be decorated in order to be called
    @ezplugins.ezplugin_method()
    def some_method(self, param1, param2):
        return f"{param1=}, {param2=}"
```

## Method Ordering

Further to decorating a method as being runnable by EZPlugins, one can also specify the order which the method is run. This is done by using `@ezplugins.ezplugin_method(order=X)`, where X is an integer.

The default plugin run order is `5000`. By not setting the order, the result would be the methods being run in an undefined random order.

```python
import ezplugins

@ezplugins.ezplugin
class MyPlugin:

    ...

    # Methods must be decorated in order to be called
    @ezplugins.ezplugin_method(order=5050)
    def some_method(self, param1, param2):
        return f"{param1=}, {param2=}"
```

# Plugin Manager

The EZPluginManager is responsible for both loading and returning plugin methods for execution.

Plugins are loaded from packages which are looked up within `PYTHONPATH`.

Packages are recursed and all plugins are loaded by instantiating the classes marked as plugins. The resulting objects are used when methods are run.

## Loading Plugins

Plugins are loaded by specifying the plugin package names. These packages are recursed and all classes decorated as being EZPlugin's are instantiated.

```python
import ezplugins

# Load plugins from mypackage.plugins and "mypackage2.plugins"
plugin_manager = ezplugins.EZPluginManager(["mypackage.plugins", "mypackage2.plugins"])
```

# Calling Plugins

Plugin methods can be called using the `.methods()` generator of the plugin manager. This will return one plugin at a time in a tuple of `(EZPluginMethod, EZPlugin)`.

The ordering of the results will depend on [Method Ordering](#method-ordering).

Taking the quickstart example, an example of running all `some_func` methods in all plugins can be found below...
```python
# Call the method some_func in each plugin
for method, _ in plugin_manager.methods(with_name="some_func"):
    result = method.run("param1", "param2")
    print(f"RESULT: {result}")
```

One can also call every single method marked as an EZPlugin method in all plugins using the following...
```python
# Call the method some_func in each plugin
for method, _ in plugin_manager.methods():
    result = method.run("param1", "param2")
    print(f"RESULT: {result}")
```

As you can see in the above examples we have a `_` in the `for`, this is the EZPlugin plugin object which we didn't need...
```python
# Call the method some_func in each plugin
for method, plugin in plugin_manager.methods(with_name="some_func"):
    result = method.run("param1", "param2")
    print(f"RESULT: {result} fomr {method.name}, plugin {plugin.fqn}")
```

## By Method Name

Plugins are generally called by method name, as seen above using the `with_name` keyword argument.

This can be omitted but the result will be every plugin method decorated as an EZPlugin method being called.

## By Method Name & Plugin Name

Restricting the method being run to a specific plugin fully qualified name, class name or alias can be achieved using the below examples...

```python
# Call the method some_func by specifying the fully qualified plugin name
for method, plugin in plugin_manager.methods(with_name="some_func", from_plugin="mypackage.plugins#MyPlugin"):
    result = method.run("param1", "param2")
    print(f"RESULT: {result} fomr {method.name}, plugin {plugin.fqn}")

# Call the method some_func by specifying the plugin class name
for method, plugin in plugin_manager.methods(with_name="some_func", from_plugin="#MyPlugin"):
    result = method.run("param1", "param2")
    print(f"RESULT: {result} fomr {method.name}, plugin {plugin.fqn}")

# Call the method some_func by specifying an alias
for method, plugin in plugin_manager.methods(with_name="some_func", from_plugin="some_alias"):
    result = method.run("param1", "param2")
    print(f"RESULT: {result} fomr {method.name}, plugin {plugin.fqn}")
```