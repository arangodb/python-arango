"""Utility functions for testing."""

import collections


def get_next_db_name(arango):
    """Generate and return the next available database name.

    The names generated look like "db0", "db1" ...

    :param arango: the arango connection object
    :type arango: arango.Arango
    :returns: the next available database name
    :rtype: str
    """
    num = 0
    while "db{}".format(num) in arango.databases["all"]:
        num += 1
    return "db{}".format(num)


def get_next_col_name(arango):
    """Generate and return the next available collection name.

    The names generated look like "col0", "col1" ...

    :param arango: the arango connection object
    :type arango: arango.Arango
    :returns: the next available collection name
    :rtype: str
    """
    num = 0
    while "col{}".format(num) in arango.collections["all"]:
        num += 1
    return "col{}".format(num)


def get_next_graph_name(arango):
    """Generate and return the next available collection naem.

    The names generated looke like "graph0", "graph1" ...

    :param arango: the arango connection object
    :type arango: arango.Arango
    :returns: the next available graph name
    :rtype: str
    """
    num = 0
    while "graph{}".format(num) in arango.collections["all"]:
        num += 1
    return "col{}".format(num)


def strip_system_keys(obj):
    """Return the document(s) with all the system keys removed.

    :param obj: document(s)
    :type obj: list or dict
    :returns: the document(s) with the system keys removed
    :rtype: list or dict
    """
    if isinstance(obj, collections.Mapping):
        return {k: v for k, v in obj.iteritems() if not k.startswith("_")}
    elif isinstance(obj, collections.Iterable):
        return [
            {k: v for k, v in document.iteritems() if not k.startswith("_")}
            for document in obj
        ]
