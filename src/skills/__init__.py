import os
import importlib
import glob

# Dynamically import all modules in the 'skills' package
modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]

for module_name in __all__:
    importlib.import_module(f".{module_name}", package=__name__)
