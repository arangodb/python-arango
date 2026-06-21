import importlib
import pkgutil

import pytest

import arango


def arango_modules():
    yield arango.__name__

    for module_info in pkgutil.walk_packages(
        arango.__path__,
        prefix=f"{arango.__name__}.",
    ):
        yield module_info.name


@pytest.mark.parametrize("module_name", sorted(arango_modules()))
def test_import_module(module_name):
    importlib.import_module(module_name)
