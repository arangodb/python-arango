from arango.version import __version__


def test_package_version():
    assert __version__.count('.', 2)
    assert all([number.isdigit() for number in __version__.split('.')])
