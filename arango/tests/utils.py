"""Utility functions used for testing."""

import collections


def generate_db_name(arango):
    """Generate and return the next available database name.

    The names look like "test_database_001", "test_database_002" ...

    :param arango: ArangoDB wrapper object
    :type arango: arango.Arango
    :returns: the next available database name
    :rtype: str
    """
    num = 0
    existing_databases = set(arango.databases["all"])
    while "test_database_{num:03d}".format(num=num) in existing_databases:
        num += 1
    return "test_database_{num:03d}".format(num=num)


def generate_col_name(arango):
    """Generate and return the next available collection name.

    The names look like "test_collection_001", "test_collection_002" ...

    :param arango: ArangoDB wrapper object
    :type arango: arango.Arango or arango.database.ArangoDatabase
    :returns: the next available collection name
    :rtype: str
    """
    num = 0
    existing_collections = set(arango.collections["all"])
    while "test_collection_{num:03d}".format(num=num) in existing_collections:
        num += 1
    return "test_collection_{num:03d}".format(num=num)


def generate_graph_name(arango):
    """Generate and return the next available collection name.

    The names look like "test_graph_001", "test_graph_002" ...

    :param arango: ArangoDB wrapper object
    :type arango: arango.Arango or arango.database.ArangoDatabase
    :returns: the next available graph name
    :rtype: str
    """
    num = 0
    existing_graphs = set(arango.graphs)
    while "test_graph_{num:03d}".format(num=num) in existing_graphs:
        num += 1
    return "test_graph_{num:03d}".format(num=num)


def generate_user_name(arango):
    """Generate and return the next available user name.

    The names generated look like "test_user_001", "test_user_002" ...

    :param arango: ArangoDB wrapper object
    :type arango: arango.Arango or arango.database.ArangoDatabase
    :returns: the next available user name
    :rtype: str
    """
    num = 0
    existing_users = set(arango.users)
    while "test_user_{num:03d}".format(num=num) in existing_users:
        num += 1
    return "test_user_{num:03d}".format(num=num)


def strip_system_keys(obj):
    """Return the document(s) with all the system keys deleted.

    :param obj: document(s)
    :type obj: list or dict
    :returns: the document(s) with the system keys deleted
    :rtype: list or dict
    """
    if isinstance(obj, collections.Mapping):
        return {k: v for k, v in obj.items() if not k.startswith("_")}
    elif isinstance(obj, collections.Iterable):
        return [
            {k: v for k, v in document.items() if not k.startswith("_")}
            for document in obj
        ]
