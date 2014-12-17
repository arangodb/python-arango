"""Utility functions for testing."""


def get_next_col_name(arango):
    """Generate and return the next available collection name."""
    num = 0
    while "col{}".format(num) in arango.collections["all"]:
        num += 1
    return "col{}".format(num)


def get_next_db_name(arango):
    """Generate and return the next available database name."""
    num = 0
    while "db{}".format(num) in arango.databases["all"]:
        num += 1
    return "db{}".format(num)