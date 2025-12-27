import os
import pkgutil
import importlib

# Get the current package path
package_path = os.path.dirname(__file__)

# Iterate over all modules in the current package
for _, module_name, _ in pkgutil.iter_modules([package_path]):
    # Import the module
    importlib.import_module(f".{module_name}", package=__name__)