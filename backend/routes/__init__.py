import importlib
import pkgutil

from flask.blueprints import Blueprint


__all__ = []

# Discover modules inside the routes package
for _, module_name, _ in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")

    # Find and export Blueprint objects ending in "_bp"
    for name, value in vars(module).items():
        if name.endswith("_bp") and isinstance(value, Blueprint):
            globals()[name] = value
            __all__.append(name)