from importlib import import_module
import pkgutil
import inspect
from typing import List, Type

"""Core module."""


try:
    from . import apps as _apps  # package containing app packages
except Exception:
    _apps = None

_MODELS_CACHE: List[Type] = []


def _collect_models() -> List[Type]:
    if not _apps:
        return []

    found = {}
    for finder, module_name, ispkg in pkgutil.walk_packages(
        path=_apps.__path__, prefix=_apps.__name__ + "."
    ):
        # We are interested in modules that are either:
        #  - app.models (a single module)
        #  - app.models.<model_module> (models package with submodules)
        if ".models" not in module_name:
            continue

        try:
            mod = import_module(module_name)
        except Exception:
            # ignore modules that fail to import
            continue

        for _, obj in inspect.getmembers(mod, inspect.isclass):
            key = f"{obj.__module__}.{obj.__name__}"
            found.setdefault(key, obj)

    # preserve deterministic order
    return list(found.values())


def get_all_models() -> List[Type]:
    """
    Return a list of all model classes discovered under the `core.apps` package.

    Scans for modules named `*.models` and `*.models.*`, imports them, and
    returns classes defined in those modules (excluding private classes).
    """
    global _MODELS_CACHE
    if not _MODELS_CACHE:
        _MODELS_CACHE = _collect_models()
    return list(_MODELS_CACHE)


__all__ = ["get_all_models"]
