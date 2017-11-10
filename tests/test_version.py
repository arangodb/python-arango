from arango.utils import VERSION


def test_package_version():
    assert VERSION.count('.', 2)
    assert all([number.isdigit() for number in VERSION.split('.')])
