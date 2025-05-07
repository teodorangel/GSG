# crawler.extractors package

import pkgutil
import importlib
from crawler.extractors.base import BaseExtractor

_extractors = None

def get_extractors() -> list[type[BaseExtractor]]:
    """
    Dynamically discover all BaseExtractor subclasses in this package.
    """
    global _extractors
    if _extractors is None:
        _extractors = []
        for finder, name, is_pkg in pkgutil.iter_modules(__path__):
            module = importlib.import_module(f"{__name__}.{name}")
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, BaseExtractor) and obj is not BaseExtractor:
                    _extractors.append(obj)
    return _extractors
