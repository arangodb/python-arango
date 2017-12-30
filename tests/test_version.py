from arango.version import __VERSION__


def test_package_version():
    assert __VERSION__.count('.', 2)
    assert all([number.isdigit() for number in __VERSION__.split('.')])
